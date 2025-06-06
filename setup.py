from setuptools import setup

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    # Nombre para pip: pip install doomlauncher-for-crispy-doom
    name='doomlauncher-for-crispy-doom',

    # Versión del paquete.
    version='0.1.0',

    author='Merkosas',

    description='Un lanzador simple para Crispy Doom y otros motores derivados, hecho con PyQt.',
    
    long_description=long_description,
    long_description_content_type="text/markdown",

    url='https://github.com/Merkosas/doomlauncher-for-crispy-doom',
    
    # Dependencias: pip instalará PyQt6 junto con tu paquete.
    install_requires=[
        'PyQt6',
    ],

    py_modules=['doom_launcher_qt'],


    entry_points={
        'console_scripts': [
            'doomlauncher=doom_launcher_qt:main',
        ],
    },
    
    # Palabras clave para que la gente encuentre tu paquete
    keywords='doom crispy-doom launcher qt',

    # Clasificadores para PyPI
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
)
