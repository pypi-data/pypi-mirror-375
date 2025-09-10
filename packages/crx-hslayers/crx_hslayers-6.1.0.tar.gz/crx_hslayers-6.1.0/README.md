# HSLayers-NG map widget for Wagtail CodeRed CMS

Note: Has npm dependency on [HSLayers-NG](https://www.npmjs.com/package/hslayers-ng-app) that gets automatically installed into static files. `python manage.py collectstatic` must be executed for the module to correctly locate the HSLayers bundles.

## Instalation

1. Install this package from PyPi using folowing command:

    ```
    $ pip install crx-hslayers wagtail-crx-block-frontend-assets
    ```

2. Add 'hslayers' and 'wagtail_crx_block_frontend_assets' to the INSTALLED_APPS list in the settings/base.py

    ```python
    INSTALLED_APPS = [
        # This project
        'website',

        # CodeRed CMS
        'coderedcms',
        'bootstrap4',
        ...
        'wagtail_crx_block_frontend_assets',
        'crx_hslayers'
    ]
    ```

3. Add MapBlock to your model, for example:
    ```python
    from wagtail.fields import StreamField
    from coderedcms.models import CoderedWebPage
    from crx_hslayers.blocks import MapBlock


    class WebPage(CoderedWebPage):  
        
        ...

        body = StreamField(
            block_types=[
                ("map_block", MapBlock())
            ],
            null=True,
            blank=True,
            use_json_field=True,
        )

        ...

    ```

4. Define place in your templates where you want your MapBlock assets to be rendered like this:
    ```django
    {% extends "coderedcms/pages/base.html" %}

    {% block custom_assets %}
    {{ block.super }}
    {% include "wagtail_crx_block_frontend_assets/includes/block_assets.html" with required_file_extension=".css" %}
    {% endblock custom_assets %}

    {% block custom_scripts %}
    {{ block.super }}
    {% include "wagtail_crx_block_frontend_assets/includes/block_assets.html" with required_file_extension=".js" %}
    {% endblock custom_scripts %}
    ```

5. Create new migration with changes made to your model
    ```
    python manage.py makemigrations
    ```

6. Now apply your new migration.
    ```
    python manage.py migrate
    ```

7. Install HSLayers app package from npm
    ```
    cd {YOUR PYTHON VENV PATH}/lib/python3.12/site-packages/crx_hslayers/static/ 
    npm install
    ```

8. Collect static files from crx-hslayers to your Wagtail site

    ```
    $ python manage.py collectstatic
    ```

## Development

Update semantic version of the package

Run test update without commiting

```
$ bumpver update --patch(--minor|--major) --dry
```

Run update and commit the changes to the repo

```
$ bumpver update --patch(--minor|--major)
```

## Manual package publishing

Delete all previous builds in the dist/\* directory.

Linux:

```
python3 -m build
python3 -m pip install --upgrade twine
python3 -m twine upload dist/*
```

Windows:

```
py -m build
py -m pip install --upgrade twine
py -m twine upload dist/*
```

Use `__token__` for the username and API token acquired at pypi.org for password.

Upload to Test PyPi:

```
python3 -m twine upload --repository testpypi dist/*
```
