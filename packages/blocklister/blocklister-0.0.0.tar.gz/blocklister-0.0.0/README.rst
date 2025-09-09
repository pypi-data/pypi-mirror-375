.. Copyright © 2025 Frederik “Freso” S. Olesen <https://freso.dk/>
.. SPDX-License-Identifier: AGPL-3.0-or-later

=============
 blocklister
=============

Command-line utility and Python library for converting blocklists between formats.

-------
 Usage
-------

(TBD…)

--------------
 Contributing
--------------

TL;DR
-----

`Behave like a decent person`_,
`install pre-commit`_,
run ``pre-commit install`` in the project root, and
take heed of any errors you get when trying to commit.

.. _`install pre-commit`: https://pre-commit.com/#installation

General
-------

The project aims to follow best practices for development. Be sure to
`behave like a decent person`_ in all interactions related to this project.

We follow a number of standards and best-practices with the aim that
on-boarding of contributors, incl. our future selves, will go more smoothly.
This includes utilizing `pre-commit`_ to automate checking a bunch of things
before code even gets committed to the repository. It is *highly* recommended
that anyone wanting to contribute enables this.

Relevant standards for code style and commit messages are specified in those sections.

.. _behave like a decent person: https://www.contributor-covenant.org/version/3/0/code_of_conduct/
.. _pre-commit: https://pre-commit.com/

REUSE
~~~~~

The `REUSE Specification`_ aims to “make licensing easy for humans and
machines alike.” This is unlikely something you will need to worry about,
but in the case where you do wish to add code from elsewhere, be sure to keep
this in mind.

.. _REUSE Specification: https://reuse.software/

Code style
----------

This project generally aims to adhere to official Python project style guidelines, such as PEP8_.
More specifically, it uses `the Black code style`_ as implemented via `Ruff`_.

.. _PEP8: https://www.python.org/dev/peps/pep-0008/
.. _the Black code style: https://black.readthedocs.io/en/stable/the_black_code_style/current_style.html
.. _Ruff: https://docs.astral.sh/ruff/

Commit style
------------

`Keep commits atomic`_ and use `Conventional Commits`_ with `good commit messages`_.

.. _`Keep commits atomic`: https://www.freshconsulting.com/insights/blog/atomic-commits/
.. _`Conventional Commits`: https://www.conventionalcommits.org/en/v1.0.0/
.. _`good commit messages`: https://cbea.ms/git-commit/

---------
 License
---------

blocklister is `free software`_: you can redistribute it and/or modify
it under the terms of the GNU Affero General Public License as
published by the Free Software Foundation, either version 3 of the
License, or (at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.
See the GNU Affero General Public License for more details.

You should have received a copy of the GNU Affero General Public License
along with this program. If not, see <https://www.gnu.org/licenses/>.

**Some parts of the repository may be distributed under different terms.**
This project adheres to the `REUSE Specification version 3.3`_ and any
files or code deviating from the general license of the project will be
annotated as such.

.. _`free software`: https://www.gnu.org/philosophy/philosophy.html
.. _`REUSE Specification version 3.3`: https://reuse.software/spec-3.3/
