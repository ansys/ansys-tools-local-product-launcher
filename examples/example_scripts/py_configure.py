# Copyright (C) 2022 - 2024 ANSYS, Inc. and/or its affiliates.
# SPDX-License-Identifier: MIT
#
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

"""
Choosing configuration at runtime
---------------------------------

"""

# %%
# Import the necessary modules

import os

from example_httpserver_plugin import LauncherConfig

from ansys.tools.local_product_launcher import launch_product

# %%
# Default configuration
# ~~~~~~~~~~~~~~~~~~~~~
#
# First, let's launch the product without any configuration. This will fall back
# to the default configuration.

product_instance = launch_product(product_name="example_httpserver")
product_instance.urls

# %%
# To ensure the server is running, we can use the ``wait`` method.
product_instance.wait(timeout=5)

# %%
# Let's retrieve the content of the server's main page. This simply serves
# a list of files in the directory where the server was launched.

import requests

res = requests.get(f"http://{product_instance.urls['main']}")
print(res.content.decode("utf-8"))

# %%
# Custom configuration
# ~~~~~~~~~~~~~~~~~~~~
#
# Now, let's try to launch the product with a custom configuration. This is done
# by passing the ``config`` and ``launch_mode`` arguments to the :func:`.launch_product`.

directory = os.path.join(os.getcwd(), "..")
product_instance = launch_product(
    product_name="example_httpserver",
    config=LauncherConfig(directory=directory),
    launch_mode="direct",
)
product_instance.urls


# %%
# Again, let's ensure the server is running.
product_instance.wait(timeout=5)

# %%
# And get the content of the main page.

full_url = f"http://{product_instance.urls['main']}"
res = requests.get(full_url)
print(res.content.decode("utf-8"))

# %%
# We can see that the server is now showing the files from the parent directory.

# %%
# Teardown
# ~~~~~~~~
#
# We can manually stop the server using the :meth:`stop <.ProductInstance.stop>` method.
# Alternatively,  the server will be stopped when all references to ``product_instance``
# are deleted.

product_instance.stop()

# %%
# To ensure the server is down, we can try to access the main page again.

try:
    requests.get(full_url)
except requests.ConnectionError:
    print("The server is down.")
