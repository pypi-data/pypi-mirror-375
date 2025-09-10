from setuptools import setup, find_packages

setup(
    name="DuckyFrameworks",            # nombre de tu paquete
    version="0.1.01",                  # versión inicial
    packages=find_packages(include=["DF*", "DF.*"]),          # busca automáticamente tus submódulos
    install_requires=[                 # dependencias externas (si tienes)
        # "kivy>=2.2.0",
    ],
    author="José Pato",
    author_email="patodequeso222@gmail.com",
    description="La libreria oficial de Ducky (no Duckyngscript) para poder usar Frameworks de manera sencilla y hay mucho de donde escojer",
    long_description=open("README.md", encoding="utf-8").read(),  # opcional
    long_description_content_type="text/markdown",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.11",
)
