.. what_is_appian_locust-inclusion-begin-do-not-remove

#######################################
What is Appian Locust?
#######################################

Appian Locust is a wrapper library around `Locust <https://locust.io>`__ for load testing Appian.
This library is intended to be used as an alternative to tools such as Jmeter and Load Runner.

Appian Locust capabilities

- Logging in and logging out
- Form interactions (filling/submitting)
- Finding and interacting with basic components on a SAIL interface
- Navigating to records/reports/sites

.. what_is_appian_locust-inclusion-end-do-not-remove


For full documentation, visit the `docs page <https://appian-locust.readthedocs.io/en/latest/>`__.

.. disclaimer-inclusion-begin-do-not-remove

**Disclaimer:**
This library is continuously evolving.
Currently the main focus is supporting essential use-cases.
We are happy to accept contributions to further extend functionality, address bug fixes and improve usability.
Please see the `Contributing <contributing.html>`__ section and feel free to reach out.

.. disclaimer-inclusion-end-do-not-remove

.. quick_start-inclusion-begin-do-not-remove

************************
Quick Installation Guide
************************

This guide helps you get up and running with the ``appian-locust`` library quickly.

We strongly recommend using ``pipenv`` and ``pyenv`` to automatically manage Python versions and environments. This ensures a clean and reproducible setup for running and developing tests with Locust.

.. note::
  💡 If you don’t want to manage environments manually, jump to the *Automatic Setup* section below.

Manual Setup
------------

1. Install appian-locust using ``pip``, for more comprehensive projects we recommend using ``pipenv``.

.. code-block:: bash

      pip install appian-locust


If using ``pipenv``, simply start from the following ``Pipfile``:

.. code-block:: toml

    [packages]
    appian-locust = {version = "*"}

    [requires]
    python_version = "3.13"

Build from source
----------------------
1. Clone the repository:

.. code-block:: bash

    git clone -o prod git@gitlab.com:appian-oss/appian-locust.git


2a. Install the library globally:

.. code-block:: bash

    pip install -e appian-locust


2b. Or within a virtual environment:

.. code-block:: bash

    pipenv install -e appian-locust

Note: It’s highly recommended that you use a virtual environment when installing python artifacts. You can follow the instructions `here <https://packaging.python.org/guides/installing-using-pip-and-virtual-environments/>`__ to install virtualenv and pip.

If you have issues installing, make sure you have the proper prerequisites installed for Locust and its dependencies.
If you're having trouble on Windows, check `here <https://github.com/locustio/locust/issues/1208#issuecomment-569693439>`__

Automatic Setup
---------------

To simplify the setup process and avoid installing Python manually, use the provided `setup.sh <https://gitlab.com/appian-oss/appian-locust/-/blob/main/setup.sh>`_ script. It will:

- Install ``pyenv`` and ``pipenv`` if they are missing.
- Install the correct Python version from the ``Pipfile``.
- Create a virtual environment.
- Install all dependencies.

1. Clone the repository:

.. code-block:: bash

    git clone -o prod git@gitlab.com:appian-oss/appian-locust.git


2. Navigate to `appian-locust` directory and make the script `setup.sh` executable:

.. code-block:: bash

    cd appian-locust/
    chmod +x setup.sh

3. Run the setup:

.. code-block:: bash

    ./setup.sh

4. After setup, activate the virtual environment:

.. code-block:: bash

    pipenv shell


Test environment setup
----------------------
Download the sample test `example_locustfile.py <https://gitlab.com/appian-oss/appian-locust/-/blob/main/examples/example_locustfile.py>`_ from the Appian Locust repo and run it.

.. code-block:: bash

    locust -f example_locustfile.py

If everything is set up correctly, you should see a link to the `Locust web interface <https://docs.locust.io/en/stable/quickstart.html#locust-s-web-interface>`_, which you can use to start test runs and view results.

* For more information about how to build the workflow for your locust test, see the `How to Write a Locust Test <how_to_write_locust_tests.html>`__ section.
* For more information on running locust tests, see the `How to Run Locust <how_to_run_locust.html>`__ section.

``appian-locust`` should now be ready to run your Locust performance tests!

Troubleshooting
----------------
* **Do not have permissions to clone appian-locust**

  * Ensure you have added you ssh key to your profile. See `here <https://docs.gitlab.com/ee/user/ssh.html#add-an-ssh-key-to-your-gitlab-account>`__ for how to do this.
* **"locust is not available"**

  * Verify that you ran ``pip install -e appian-locust``
* **"Failed to establish a new connection: [Errno 8] nodename nor servname provided, or not known"**

  * check that ``host_address`` is specified correctly in your locust test file.

* **"Login unsuccessful, no multipart cookie found...make sure credentials are correct"**

  * check that `auth` specifies a valid username and password combination for the site you're testing on in your locust test file.

* **"General request and response debugging"**

  * Add ``self.client.record_mode = True`` to your ``HttpUser`` subclass.  Files will be placed in ``/record_responses`` where the runner is executed.

  * Use ``run_single_user`` method of locust to run in debugger mode.

.. quick_start-inclusion-end-do-not-remove
