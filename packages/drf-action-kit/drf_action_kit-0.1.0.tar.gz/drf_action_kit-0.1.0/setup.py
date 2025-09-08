from setuptools import find_packages, setup

setup(
    name="drf-action-kit",
    version="0.1.0",
    packages=find_packages(),
    install_requires=["djangorestframework>=3.14.0"],
    description="Action-based serializers for DRF for all view types",
    author="Erdi Mollahüseyinoğlu",
    url="https://github.com/erdimollahuseyin/drf-action-kit",
    classifiers=[
        "Programming Language :: Python :: 3",
        "Framework :: Django",
        "Framework :: Django REST Framework",
    ],
)
