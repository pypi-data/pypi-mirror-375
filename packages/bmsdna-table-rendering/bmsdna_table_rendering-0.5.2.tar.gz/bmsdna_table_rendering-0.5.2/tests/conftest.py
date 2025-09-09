import pytest
import os
from pathlib import Path


@pytest.fixture(scope="session")
def spark_session():
    if os.getenv("NO_SPARK", "0") == "1":
        return None
    if os.getenv("ODBCLAKE_TEST_CONFIGURATION", "spark").lower() != "spark":
        return None
    from pyspark.sql import SparkSession

    jar = str(Path("tests/jar").absolute())
    builder = (
        SparkSession.builder.appName("test_spark")  # type: ignore
        .config("spark.driver.extraClassPath", jar)
        .config("spark.executor.extraClassPath", jar)
        .config("spark.memory.fraction", 0.5)
    )

    spark = builder.getOrCreate()

    return spark
