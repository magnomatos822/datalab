"""
Funções analíticas para processamento de dados com Spark
"""

import mlflow
import mlflow.spark
from pyspark.ml.classification import LogisticRegression, RandomForestClassifier
from pyspark.ml.evaluation import BinaryClassificationEvaluator, RegressionEvaluator
from pyspark.ml.feature import StandardScaler, VectorAssembler
from pyspark.ml.regression import LinearRegression, RandomForestRegressor
from pyspark.ml.tuning import CrossValidator, ParamGridBuilder
from pyspark.sql import SparkSession
from pyspark.sql.functions import avg, col, count, expr, lag, rank, sum, window
from pyspark.sql.types import DoubleType, IntegerType
from pyspark.sql.window import Window


class DataAnalyzer:
    """Classe base para analisadores de dados"""

    def __init__(self, spark=None):
        """
        Inicializa o analisador

        Args:
            spark: Sessão Spark existente ou None para criar uma nova
        """
        if spark is None:
            self.spark = (
                SparkSession.builder.appName("DataAnalyzer")
                .config(
                    "spark.sql.extensions", "io.delta.sql.DeltaSparkSessionExtension"
                )
                .config(
                    "spark.sql.catalog.spark_catalog",
                    "org.apache.spark.sql.delta.catalog.DeltaCatalog",
                )
                .getOrCreate()
            )
        else:
            self.spark = spark

        self.data = None

    def load_data(self, path, format="delta"):
        """
        Carrega dados para análise

        Args:
            path: Caminho para os dados
            format: Formato dos dados (delta, csv, parquet, etc)
        """
        self.data = self.spark.read.format(format).load(path)
        print(f"Dados carregados: {self.data.count()} registros")
        return self.data

    def describe(self):
        """Retorna estatísticas descritivas básicas"""
        if self.data is None:
            raise ValueError("Dados não carregados. Use load_data() primeiro.")

        return self.data.describe()

    def get_schema(self):
        """Retorna o esquema dos dados"""
        if self.data is None:
            raise ValueError("Dados não carregados. Use load_data() primeiro.")

        return self.data.printSchema()

    def filter_data(self, condition):
        """
        Filtra os dados com base em uma condição

        Args:
            condition: Condição de filtro (expressão SQL ou coluna)
        """
        if self.data is None:
            raise ValueError("Dados não carregados. Use load_data() primeiro.")

        self.data = self.data.filter(condition)
        return self.data


class TimeSeriesAnalyzer(DataAnalyzer):
    """Analisador para séries temporais"""

    def __init__(self, spark=None):
        """Inicializa o analisador de séries temporais"""
        super().__init__(spark)

    def analyze(self, date_column="date", metric_column=None, period=30):
        """
        Realiza análise básica de séries temporais

        Args:
            date_column: Nome da coluna de data
            metric_column: Nome da coluna de métrica a analisar
            period: Período para calcular médias móveis
        """
        if self.data is None:
            raise ValueError("Dados não carregados. Use load_data() primeiro.")

        # Se coluna métrica não for especificada, usa a primeira coluna numérica
        if metric_column is None:
            numeric_cols = [
                f.name
                for f in self.data.schema.fields
                if isinstance(f.dataType, (DoubleType, IntegerType))
            ]
            if not numeric_cols:
                raise ValueError("Nenhuma coluna numérica encontrada nos dados.")
            metric_column = numeric_cols[0]

        # Garantir que a coluna de data está ordenada
        df = self.data.orderBy(date_column)

        # Calcular estatísticas básicas por dia
        daily_stats = df.groupBy(date_column).agg(
            avg(col(metric_column)).alias("avg"),
            sum(col(metric_column)).alias("sum"),
            count(col(metric_column)).alias("count"),
        )

        # Calcular médias móveis
        window_spec = Window.orderBy(date_column).rowsBetween(-period, 0)

        with_moving_avg = daily_stats.withColumn(
            f"moving_avg_{period}", avg(col("avg")).over(window_spec)
        )

        # Calcular variação percentual
        window_lag = Window.orderBy(date_column)
        with_pct_change = with_moving_avg.withColumn(
            "prev_value", lag(col("avg"), 1).over(window_lag)
        ).withColumn(
            "pct_change", ((col("avg") - col("prev_value")) / col("prev_value")) * 100
        )

        return with_pct_change

    def detect_anomalies(self, date_column="date", metric_column=None, threshold=3.0):
        """
        Detecta anomalias em séries temporais usando o método do Z-score

        Args:
            date_column: Nome da coluna de data
            metric_column: Nome da coluna de métrica a analisar
            threshold: Limiar de Z-score para considerar anomalia
        """
        if self.data is None:
            raise ValueError("Dados não carregados. Use load_data() primeiro.")

        # Se coluna métrica não for especificada, usa a primeira coluna numérica
        if metric_column is None:
            numeric_cols = [
                f.name
                for f in self.data.schema.fields
                if isinstance(f.dataType, (DoubleType, IntegerType))
            ]
            if not numeric_cols:
                raise ValueError("Nenhuma coluna numérica encontrada nos dados.")
            metric_column = numeric_cols[0]

        # Calcular estatísticas
        stats = self.data.select(
            avg(col(metric_column)).alias("mean"),
            expr(f"stddev({metric_column})").alias("stddev"),
        ).collect()[0]

        mean_val = stats["mean"]
        stddev_val = stats["stddev"]

        # Detectar anomalias
        anomalies = self.data.withColumn(
            "z_score", abs((col(metric_column) - lit(mean_val)) / lit(stddev_val))
        ).withColumn("is_anomaly", col("z_score") > threshold)

        return anomalies.filter(col("is_anomaly") == True)

    def forecast(self, date_column="date", metric_column=None, periods=7):
        """
        Realiza previsão simples com regressão linear

        Args:
            date_column: Nome da coluna de data
            metric_column: Nome da coluna de métrica a prever
            periods: Número de períodos para prever
        """
        if self.data is None:
            raise ValueError("Dados não carregados. Use load_data() primeiro.")

        # Se coluna métrica não for especificada, usa a primeira coluna numérica
        if metric_column is None:
            numeric_cols = [
                f.name
                for f in self.data.schema.fields
                if isinstance(f.dataType, (DoubleType, IntegerType))
            ]
            if not numeric_cols:
                raise ValueError("Nenhuma coluna numérica encontrada nos dados.")
            metric_column = numeric_cols[0]

        # Converter data para índice numérico
        from pyspark.sql.functions import to_timestamp, unix_timestamp

        indexed_df = self.data.withColumn(
            "timestamp", unix_timestamp(col(date_column))
        ).withColumnRenamed(metric_column, "target")

        # Preparar recursos para o modelo
        feature_assembler = VectorAssembler(
            inputCols=["timestamp"], outputCol="features"
        )

        # Criar e treinar o modelo
        lr = LinearRegression(featuresCol="features", labelCol="target")

        pipeline_data = feature_assembler.transform(indexed_df)
        model = lr.fit(pipeline_data)

        # Gerar timestamps para previsão
        last_timestamp = indexed_df.agg({"timestamp": "max"}).collect()[0][0]
        day_seconds = 86400  # segundos em um dia

        # Criar dataframe para previsão
        future_timestamps = [
            (last_timestamp + (i + 1) * day_seconds,) for i in range(periods)
        ]
        future_df = self.spark.createDataFrame(future_timestamps, ["timestamp"])

        # Preparar features e fazer previsão
        future_features = feature_assembler.transform(future_df)
        predictions = model.transform(future_features)

        return predictions.select("timestamp", "prediction")


class PredictiveAnalyzer(DataAnalyzer):
    """Analisador para modelagem preditiva"""

    def __init__(self, spark=None):
        """Inicializa o analisador preditivo"""
        super().__init__(spark)
        self.model = None

        # Configurar MLflow
        mlflow.set_tracking_uri("http://mlflow:5000")

    def prepare_features(self, feature_cols, label_col, categorical_cols=None):
        """
        Prepara recursos para modelagem

        Args:
            feature_cols: Lista de colunas de recursos
            label_col: Coluna alvo
            categorical_cols: Lista de colunas categóricas para codificar
        """
        if self.data is None:
            raise ValueError("Dados não carregados. Use load_data() primeiro.")

        # Tratamento de colunas categóricas iria aqui
        # (Seria implementado com StringIndexer e OneHotEncoder)

        # Montar vetor de recursos
        assembler = VectorAssembler(inputCols=feature_cols, outputCol="features")

        # Escalonar recursos
        scaler = StandardScaler(
            inputCol="features",
            outputCol="scaled_features",
            withStd=True,
            withMean=True,
        )

        # Aplicar transformações
        assembled_data = assembler.transform(self.data)
        self.prepared_data = scaler.fit(assembled_data).transform(assembled_data)

        # Renomear coluna alvo
        self.prepared_data = self.prepared_data.withColumnRenamed(label_col, "label")

        return self.prepared_data

    def train_test_split(self, test_ratio=0.2, seed=42):
        """
        Divide dados em conjuntos de treino e teste

        Args:
            test_ratio: Proporção do conjunto de teste
            seed: Semente para reprodutibilidade
        """
        if not hasattr(self, "prepared_data"):
            raise ValueError("Dados não preparados. Use prepare_features() primeiro.")

        train_data, test_data = self.prepared_data.randomSplit(
            [1 - test_ratio, test_ratio], seed=seed
        )
        self.train_data = train_data
        self.test_data = test_data

        print(f"Dados de treino: {train_data.count()} registros")
        print(f"Dados de teste: {test_data.count()} registros")

        return train_data, test_data

    def train_regression(self, model_type="linear", params=None):
        """
        Treina um modelo de regressão

        Args:
            model_type: Tipo de modelo ('linear' ou 'random_forest')
            params: Parâmetros do modelo
        """
        if not hasattr(self, "train_data"):
            raise ValueError("Dados não divididos. Use train_test_split() primeiro.")

        # Iniciar experimento MLflow
        with mlflow.start_run(run_name=f"{model_type}_regression"):
            # Selecionar tipo de modelo
            if model_type == "linear":
                model = LinearRegression(
                    featuresCol="scaled_features", labelCol="label"
                )
                if params:
                    model.setParams(**params)
                mlflow.log_param("model_type", "LinearRegression")
            elif model_type == "random_forest":
                model = RandomForestRegressor(
                    featuresCol="scaled_features", labelCol="label"
                )
                if params:
                    model.setParams(**params)
                mlflow.log_param("model_type", "RandomForestRegressor")
            else:
                raise ValueError(f"Tipo de modelo desconhecido: {model_type}")

            # Treinar modelo
            self.model = model.fit(self.train_data)

            # Avaliar no conjunto de teste
            predictions = self.model.transform(self.test_data)

            # Métricas
            evaluator = RegressionEvaluator(
                labelCol="label", predictionCol="prediction"
            )
            rmse = evaluator.setMetricName("rmse").evaluate(predictions)
            mae = evaluator.setMetricName("mae").evaluate(predictions)
            r2 = evaluator.setMetricName("r2").evaluate(predictions)

            # Registrar métricas no MLflow
            mlflow.log_metrics({"rmse": rmse, "mae": mae, "r2": r2})

            # Salvar modelo
            mlflow.spark.log_model(self.model, "model")

            print(f"Modelo treinado com RMSE: {rmse:.4f}, MAE: {mae:.4f}, R²: {r2:.4f}")

            return self.model, {"rmse": rmse, "mae": mae, "r2": r2}

    def train_classification(self, model_type="logistic", params=None):
        """
        Treina um modelo de classificação

        Args:
            model_type: Tipo de modelo ('logistic' ou 'random_forest')
            params: Parâmetros do modelo
        """
        if not hasattr(self, "train_data"):
            raise ValueError("Dados não divididos. Use train_test_split() primeiro.")

        # Iniciar experimento MLflow
        with mlflow.start_run(run_name=f"{model_type}_classification"):
            # Selecionar tipo de modelo
            if model_type == "logistic":
                model = LogisticRegression(
                    featuresCol="scaled_features", labelCol="label"
                )
                if params:
                    model.setParams(**params)
                mlflow.log_param("model_type", "LogisticRegression")
            elif model_type == "random_forest":
                model = RandomForestClassifier(
                    featuresCol="scaled_features", labelCol="label"
                )
                if params:
                    model.setParams(**params)
                mlflow.log_param("model_type", "RandomForestClassifier")
            else:
                raise ValueError(f"Tipo de modelo desconhecido: {model_type}")

            # Treinar modelo
            self.model = model.fit(self.train_data)

            # Avaliar no conjunto de teste
            predictions = self.model.transform(self.test_data)

            # Métricas
            evaluator = BinaryClassificationEvaluator(labelCol="label")
            auc = evaluator.evaluate(predictions)

            # Registrar métricas no MLflow
            mlflow.log_metrics({"auc": auc})

            # Salvar modelo
            mlflow.spark.log_model(self.model, "model")

            print(f"Modelo treinado com AUC: {auc:.4f}")

            return self.model, {"auc": auc}
