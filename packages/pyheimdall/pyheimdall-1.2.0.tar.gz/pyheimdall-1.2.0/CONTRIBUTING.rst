##########
pyHeimdall
##########


************
Introduction
************

First off, thank you for considering contributing to pyHeimdall. 
Please take a moment to review this document in order to make the contribution process easy and effective for everyone involved.

Following these guidelines helps to communicate that you respect the time of the other contributors.
In return, they'd reciprocate by trying to addressing your issue, assessing changes, or helping you however they are able to.

This is a free software and we love to receive contributions from our community — you!
There are many ways to contribute, from writing tutorials or improving the documentation, to submitting bug reports and feature requests or writing code to improve pyHeimdall or `one of its connectors <https://gitlab.huma-num.fr/datasphere/heimdall/connectors>`_.
No big commitment required; even if all you do is point out an anomaly, give your opinion or fix a typo, you are a contributor.

As for everything else in the project, the contributions are governed by our code of conduct of respect, collaboration, sobriety and overall non-bullshittery and non-dickheadness.
`Here is an example <https://policies.python.org/python.org/code-of-conduct/>`_ if you need one.



************
Ground rules
************

Asking questions, reporting bugs
================================

Please, don't send us emails for questions, bug reports or general social activities related to the project.
For the sake of `FAIRness <https://www.go-fair.org/fair-principles/>`_ and to *not* increase the workload of other contributors, all these should happen `in public issues <https://gitlab.huma-num.fr/datasphere/heimdall/python/-/issues/>`_.

When `filling a new issue <https://gitlab.huma-num.fr/datasphere/heimdall/python/-/issues/new>`_, make sure to answer these five questions:

#. What version of Python are you using (``python --version``)?
#. Do you use the latest version of the software (``pip install --upgrade .``)?
#. What did you do?
#. What did you expect to see?
#. What did you see instead?



Modifying the software
======================

Changes are welcome via `GitLab merge requests <https://docs.gitlab.com/ee/user/project/merge_requests/>`_.
If you are new to the project and looking for a way to get involved, try picking up `an issue with the "up-for-grabs" label <https://gitlab.huma-num.fr/datasphere/heimdall/python/-/issues/?sort=created_date&state=all&label_name%5B%5D=up-for-grabs>`_.
Hints about what needs to be done are usually provided.

Another good place for finding (or confirming an) inspiration is `the project roadmap <https://gitlab.huma-num.fr/datasphere/heimdall/python/-/milestones>`_.

For all merge requests, please respect the following guidelines:

- Each merge request should implement *one* feature or bugfix.
  If you want to add or fix more than one thing, submit more than one pull request.
- Keep it simple and self-contained.
  Don't add stuff to the codebase unless absolutely needed.
  For example, err on the side of using simple functions rather than huge classes.
  Modify only files that are irrelevant to your feature or bugfix.
- Do not add dependencies to the project.
- Ensure cross-version and cross-platform compatibility.
- Ensure your code that goes is compliant with the `PEP-8 style guide <https://peps.python.org/pep-0008/>`_.
  This can easily be verified using the ``pycodestyle`` tool.
- Fully cover and specify your code with automated tests, and make sure you don't break any existing test.
  This can easily be verified using the ``pytest`` and ``coverage`` tools.
- Don't forget agree to the `DCO <https://en.wikipedia.org/wiki/Developer_Certificate_of_Origin>`_ in each commit.
  This can easily be done using the ``--signoff`` `Git option <https://stackoverflow.com/questions/1962094/what-is-the-sign-off-feature-in-git-for>`_.

Small contributions, where the content is small enough to not be considered intellectual property, can be submitted as a patch.
We're talking about obvious fixes that do not introduce any new functionality or creative thinking.
Some likely examples include the following:

- Spelling / grammar fixes, typo correction, white space and formatting changes
- Comment clean up
- Adding logging messages or debugging output

Feel free to `ask for help <https://gitlab.huma-num.fr/datasphere/heimdall/python/-/issues/new>`_.
Everyone was a beginner at first!

**********
Governance
**********

This software use the governance model `detailled here <https://datasphere.readthedocs.io/en/latest/design/governance.html>`_.

Appropriate communication channels are as detailled in previous sections.
Namely, don't send emails.
Instead, use issues and merge requests of the project `main repository <https://datasphere.readthedocs.io/en/latest/design/governance.html>`_.
Use the guidelines detailled in this document.

Project members are:

- Contributors: https://gitlab.huma-num.fr/datasphere/heimdall/python/-/graphs/main
- Maintainers: https://gitlab.huma-num.fr/datasphere/heimdall/python/-/project_members
- Steering comitee: @rwitz (chairman and only member ｡ﾟ( ﾟஇ‸இﾟ)ﾟ｡ )


********************************
Follow-up and resource materials
********************************

- `Heimdall documentation <https://datasphere.readthedocs.io/projects/heimdall/>`_
- `Heimdall roadmap <https://gitlab.huma-num.fr/datasphere/heimdall/python/-/milestones>`_
- `Guidelines for non-code contributions to open source projects <https://opensource.com/life/16/1/8-ways-contribute-open-source-without-writing-code>`_
- `Working Open Guide: Mechanics of Contributing <https://mozillascience.github.io/leadership-training/03.1-mechanics.html>`_
- `First timers only <https://www.firsttimersonly.com/>`_

The last 2 resources talk about GitHub which is, in the context of research software, just an overall inferior version of GitLab.
The majority of what you'd read about GitHub in those pages applies to GitLab too.
