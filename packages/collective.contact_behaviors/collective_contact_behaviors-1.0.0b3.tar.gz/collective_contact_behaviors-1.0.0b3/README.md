<div align="center"><img alt="logo" src="https://raw.githubusercontent.com/collective/collective.contact_behaviors/main/docs/logo.svg" width="100" /></div>

<h1 align="center">Contact Behaviors for Plone</h1>

<div align="center">

[![PyPI](https://img.shields.io/pypi/v/collective.contact_behaviors)](https://pypi.org/project/collective.contact_behaviors/)
[![PyPI - Python Version](https://img.shields.io/pypi/pyversions/collective.contact_behaviors)](https://pypi.org/project/collective.contact_behaviors/)
[![PyPI - Wheel](https://img.shields.io/pypi/wheel/collective.contact_behaviors)](https://pypi.org/project/collective.contact_behaviors/)
[![PyPI - License](https://img.shields.io/pypi/l/collective.contact_behaviors)](https://pypi.org/project/collective.contact_behaviors/)
[![PyPI - Status](https://img.shields.io/pypi/status/collective.contact_behaviors)](https://pypi.org/project/collective.contact_behaviors/)


[![PyPI - Plone Versions](https://img.shields.io/pypi/frameworkversions/plone/collective.contact_behaviors)](https://pypi.org/project/collective.contact_behaviors/)

[![CI](https://github.com/collective/collective.contact_behaviors/actions/workflows/main.yml/badge.svg)](https://github.com/collective/collective.contact_behaviors/actions/workflows/main.yml)
![Code Style](https://img.shields.io/badge/Code%20Style-Black-000000)

[![GitHub contributors](https://img.shields.io/github/contributors/collective/collective.contact_behaviors)](https://github.com/collective/collective.contact_behaviors)
[![GitHub Repo stars](https://img.shields.io/github/stars/collective/collective.contact_behaviors?style=social)](https://github.com/collective/collective.contact_behaviors)

</div>

## Features

`collective.contact_behaviors` is a collection of additional behaviors and vocabularies for Dexterity content types.

### Behaviors

* `collective.contact_behaviors.address_info`: Provides address information fields:

    * address
    * address_2
    * city
    * state
    * postal_code
    * country

* `collective.contact_behaviors.contact_info`: Provides contact information fields:

    * contact_email
    * contact_website
    * contact_phone


### Permissions

| id | title | Usage |
| -- | -- | -- |
| collective.contact_behaviors.address_info.view | collective.contact_behaviors: View Basic Address Information | Read access to `city`, `state`, `postal_code`, `country` |
| collective.contact_behaviors.address_info_details.view | collective.contact_behaviors: View Detailed Address Information | Read access to `address`, `address_2` |
| collective.contact_behaviors.contact_info.view | collective.contact_behaviors: View Contact Information | Read access to `contact_email`, `contact_website`, `contact_phone` |


### Catalog Indexes

This package adds Indexes and Metadata to Portal Catalog.

| Content Attribute | Index Type | Metadata |
| -- | -- | -- |
| country | FieldIndex | ✅ |
| contact_email | FieldIndex | ❌ |

## See it in action

This package is being used by the following add-ons:

* [`collective.casestudy`](https://github.com/collective/collective.casestudy)

## Documentation

This package is supposed to be used by Plone integrators on their add-ons.

### Installation

Add `collective.contact_behaviors` as a dependency on your package's `setup.py`

```python
    install_requires = [
        "collective.contact_behaviors",
        "Plone",
        "plone.restapi",
        "setuptools",
    ],
```

Also, add `collective.contact_behaviors` to your package's `configure.zcml` (or `dependencies.zcml`):

```xml
<include package="collective.contact_behaviors" />
```

### Generic Setup

To automatically enable this package when your add-on is installed, add the following line inside the package's `profiles/default/metadata.xml` `dependencies` element:

```xml
    <dependency>profile-collective.contact_behaviors:default</dependency>
```

And to enable the behaviors provided here to a specific content type, please edit your type configuration and include the following lines (or one of them) to the `behaviors` property:

```xml
    <element value="collective.contact_behaviors.address_info" />
    <element value="collective.contact_behaviors.contact_info" />
```

## Source Code and Contributions

We welcome contributions to `collective.contact_behaviors`.

You can create an issue in the issue tracker, or contact a maintainer.

- [Issue Tracker](https://github.com/collective/collective.contact_behaviors/issues)
- [Source Code](https://github.com/collective/collective.contact_behaviors/)


### Development setup

You need a working Python environment version 3.8 or later.

Then install the dependencies and a development instance using:

```bash
make install
```

By default, we use the latest Plone version in the 6.x series.

### Update translations

```bash
make i18n
```
### Format codebase

```bash
make format
```
### Run tests

```bash
make test
```

## License

The project is licensed under GPLv2.
