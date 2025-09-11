from setuptools import setup, find_packages

setup(
    name='aplicacion_ventas_ramirez',
    version='0.1.0',
    author='Diego Ramirez Garcia',
    author_email='ramirez.garcia@gmail.com',
    description='Paquete para gestionar ventas, precios, impuestos y descuentos',
    long_description=open('README.md', encoding='utf-8').read(),
    long_description_content_type='text/markdown',
    url='https://github.com/curso_python_camara/gestor/aplicacionventas',
    packages=find_packages(),
    install_requires=[],
    classifiers=[
        'Programming Language :: Python :: 3.13',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
    python_requires='>=3.7'
)
