from setuptools import setup, find_packages

setup(
    name="idh",
    version="0.1.0",
    packages=find_packages(),
    install_requires=["requests"],
    description="API client for IDH",
    author="Faceless Developer & BPCommunity",
    author_email="faceless@dev.null",  
    url="https://t.me/FacelessDeveloper", 
    project_urls={
        "Telegram": "https://t.me/FacelessDeveloper",
        "Support": "https://t.me/FacelessWorker",
        "Channel": "https://t.me/BotProgrammerCommunity"
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
    ],
)
