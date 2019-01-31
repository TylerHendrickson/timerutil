FROM python:3.7-alpine
WORKDIR /code
RUN ["pip", "install", "-U", "pip", "setuptools", "twine", "wheel"]
CMD ["python", "setup.py", "sdist", "bdist_wheel"]
CMD ["twine", "upload", "dist/*", \
    "--repository-url", "https://$ARTIFACTORY_BASE_URL/api/pypi/$ARTIFACTORY_LOCAL_REPO", \
    "--username", "$ARTIFACTORY_USER", \
    "--password", "$ARTIFACTORY_API_KEYz" \
]
