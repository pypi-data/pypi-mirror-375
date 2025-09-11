# deSEAsion

deSEAsion is a collaborative support tool for maritime decision making.

## deseasion-backend

This package contains its backend, as the namespace package `deseasion.backend`.
It can be installed simply:

```bash
pip install deseasion-backend
```

Alternatively, you can install it from its source repository:

```bash
git clone https://gitlab.com/decide.imt-atlantique/deseasion.git
cd deseasion/backend
pip install .
```

It is not meant to be used outside a docker container with the whole application stack.
We are only distributing this package so the backend can be easily expanded by users with specific needs for which the generic deSEAsion backend is not enough.

However, you can test the backend easily. It needs an `instance/config.py` file in the directory in which you will run it which you can either copy from `deseasion/backend/instance-example` or generate from the `deseasion/backend` directory using the bash script `configure-backend.sh`.
In the latter case, you will need to supply at least the following environment variables:

```bash
DB_URI             # URI of the Postgresql/PostGIS database
CELERY_BROKER_URL  # URL of the Redis broker used by celery to communicate with the backend
```

Once setup, you can run the backend with:

```bash
python -m deseasion.backend.app
# or
ENV FLASK_APP=deseasion.backend.app
flask run
```

You can run a celery worker from the same directory (sharing the same `instance/config.py` file) with:

```bash
celery -A deseasion.backend.app.celery worker
```

## Copyright and licence

deSEAsion is copyrighted (C) 2016-2025 by IMT Atlantique Bretagne Pays de la Loire
and Service hydrographique et océanographique de la marine (Shom).
Licensed under the European Union Public Licence (EUPL) v1.2.

Please refer to the file LICENCE containing the text of the EUPL v1.2.

You may also obtain a copy of the license at:
https://joinup.ec.europa.eu/software/page/eupl

For more information on this license, please refer to:

  - European Union Public Licence:
    https://joinup.ec.europa.eu/collection/eupl/eupl-guidelines-faq-infographics


## Documentation

See the [documentation](https://deseasion-2227c9.gitlab.io) if you need any information
about the project, how to install or contribute to it.