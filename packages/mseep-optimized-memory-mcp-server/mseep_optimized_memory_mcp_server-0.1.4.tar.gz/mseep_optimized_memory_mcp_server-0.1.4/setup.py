from setuptools import setup, find_packages

setup(
    name="mseep-optimized-memory-mcp-server",
    version="0.1.4",
    packages=find_packages(    long_description="Package managed by MseeP.ai",
    long_description_content_type="text/plain",
),
    install_requires=[
        "aiofiles>=23.2.1",
        "mcp>=1.1.2",
        "aiosqlite>=0.20.0",
    ],
    python_requires=">=3.12",
    long_description="Package managed by MseeP.ai",

    long_description_content_type="text/plain",

)
