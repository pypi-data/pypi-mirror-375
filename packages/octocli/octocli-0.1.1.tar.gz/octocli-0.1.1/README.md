<a id="readme-top"></a>



<!-- PROJECT LOGO -->
<br />
<div align="center">
    <a href="https://pypi.org/project/octocli/">
        <img src="assets/logo.png" alt="Logo" width="80" height="80" />
    </a>
    <h3 align="center">OCTO CLI</h3>
    <p align="center">
        Command Line Interface to manage FastAPI projects.
        <br />
        <a href="https://github.com/samuelbagatelli/octocli/tree/main"><strong>Explore the docs »</strong></a>
        <br />
        <br />
        <a href="https://pypi.org/project/octocli/">View Demo</a>
        &middot;
        <a href="https://github.com/samuelbagatelli/octocli/issues">Report Bug</a>
    </p>
</div>



<!-- TABLE OF CONTENTS -->
<details>
    <summary>Table of Contents</summary>
    <ol>
        <li>
            <a href="#about-the-project">About The Project</a>
            <ul>
                <li><a href="#build-with">Built With</a></li>
                <li><a href="#description">Description</a></li>
            </ul>
        </li>
        <li>
            <a href="#getting-started">Getting Started</a>
            <ul>
                <li><a href="#prerequisites">Prerequisites</a></li>
                <li><a href="#installation">Installation</a></li>
            </ul>
        </li>
        <li>
            <a href="#usage">Usage</a>
        </li>
        <li>
            <a href="#roadmap">Roadmap</a>
        </li>
        <li>
            <a href="#contributing">Contributing</a>
        </li>
        <li>
            <a href="#license">License</a>
        </li>
    </ol>
</details>



<!-- ABOUT THE PROJECT -->
## About The Project

![octocli example][usage-example]

The OCTO CLI is made to manage a FastAPI advanced projetc, following the patterns used on CPID.

Default folder structure:
```
project/
├── app/
│   ├── main.py
│   ├── models/
│   │   └── model.py
│   ├── prefix/
│   │   └── prefix_base.py
│   ├── routers/
│   │   └── route.py
│   ├── schemas/
│   │   └── schema.py
│   └── settings/
│       ├── .env
│       ├── config.py
│       └── database.py
├── requirements.txt
└── README.md
```

The models use the SQLAlchemy ORM declarative mapping version of representation. Where the `prefix/prefix_base.py` contains a version of the

```python
class Base(DeclarativeBase):
    pass
```

<p align="right">(<a href="#readme-top">back to top</a>)</p>



### Description

OCTO CLI is a powerful command-line interface (CLI) tool to initiate, manage, and escalate your FastAPI projects. Focused on an advanced architecture with SQLAlchemy for data access and Pydantic for validation, the CLI automates repetitive tasks and promotes development best practices, allowing you to concentrate on the logic of your application.

#### **Key Features**

- **Quick Project Startup:** Create a complete, production-ready project structure with a single command.
- **Intelligent Code Generation:** Automate the creation of SQLAlchemy models, Pydantic schemas, and API endpoints.
- **Modular and Scalable Structure:** Organize your code in a logical and cohesive way, prepared for growth.

<p align="right">(<a href="#readme-top">back to top</a>)</p>



### Built With

* [![Typer][typer]][typer-url]
* [![Pydantic][pydantic]][pydantic-url]
* [![Jinja2][jinja]][jinja-url]

<p align="right">(<a href="#readme-top">back to top</a>)</p>



<!-- GETTING STARTED -->
## Getting Started

Some instructions to get the CLI on your terminal.

### Prerequisites

* [![Python][python]][python-url]
* [![Pip][pip]][pip-url]

### Installation

1. Install OCTO via pip (locally)

    ```sh
    pip install octocli
    ```

* For an global installation, use:
  
    ```sh
    sudo pip install octocli
    ```

<p align="right">(<a href="#readme-top">back to top</a>)</p>



<!-- USAGE EXAMPLES -->
## Usage

<!-- TODO: insert usage cases and add an /docs -->

<p align="right">(<a href="#readme-top">back to top</a>)</p>



<!-- CONTRIBUTING -->
## Contributing

Create an issue and wait. ;)

Or, fork the project and go on.

<p align="right">(<a href="#readme-top">back to top</a>)</p>



<!-- LICENSE -->
## License

Distributed under the <project_license>. See `LICENSE.txt` for more information.

<p align="right">(<a href="#readme-top">back to top</a>)</p>



<!-- MARKDOWN LINKS & IMAGES -->
[usage-example]: assets/usage-example.gif
[typer]: https://img.shields.io/badge/typer-060608?style=for-the-badge&logo=typer&logoColor=white
[typer-url]: https://typer.tiangolo.com/
[pydantic]: https://img.shields.io/badge/pydantic-E92063?style=for-the-badge&logo=pydantic
[pydantic-url]: https://docs.pydantic.dev/2.0/
[jinja]: https://img.shields.io/badge/jinja-7E0C1B?style=for-the-badge&logo=jinja&logoColor=white
[jinja-url]: https://jinja.palletsprojects.com/en/stable/
[python]: https://img.shields.io/badge/python-1E415E?style=for-the-badge&logo=python&logoColor=white
[python-url]: https://www.python.org/
[pip]: https://img.shields.io/badge/pip-0073B7?style=for-the-badge&logo=pypi&logoColor=white
[pip-url]: https://pypi.org/