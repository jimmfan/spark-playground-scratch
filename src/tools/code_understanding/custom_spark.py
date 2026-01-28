class SparkSession_custom(SparkSession):

    def __init__():
        spark = custom_spark_function(
            total_memory=total_memory,
            total_cpu=total_cpu,
            appName=appName,
            **kwargs
        )
        super(sparksession, self)__init__(sparkContext=spark.sparkContext, jsparkSession=spark._jsparkSession)
        os.putenv("HADOOP_CONF_DIR", 'etc/spark/conf/yarn-conf/*:/etc/hive/conf')
