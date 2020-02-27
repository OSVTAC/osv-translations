# Open Source Voting Translation Manager (OTM)

[This is an official project of San Francisco's [Open Source Voting System
Technical Advisory Committee][osvtac] (aka OSVTAC or TAC for short).]

This project contains translations of phrases that occur in TAC's
[demo results template][demo-template], along with a script to help with
managing these translations.

The YAML files in this repo contain the source translation data (one
file per language) and are meant to be edited by hand.
The `translations.json` file is the "built" form of the translation data
and is the primary artifact exposed by this repo for external use.

This repository is included as a [Git submodule][git-submodule] of TAC's
[open source results reporter][orr].


## Usage

```
python manage.py CMD
```

To update / regenerate the `translations.json` file:

```
python manage.py build_json
```


## Copyright

Copyright (C) 2020  Chris Jerdonek


## License

This file is part of Open Source Voting Translation Manager (OTM).

OTM is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <https://www.gnu.org/licenses/>.


## Contact

The authors can be reached at--

* Chris Jerdonek <chris.jerdonek@gmail.com>


[demo-template]: https://github.com/OSVTAC/osv-results-reporter/tree/master/templates/demo-template
[git-submodule]: https://git-scm.com/book/en/v2/Git-Tools-Submodules
[orr]: https://github.com/OSVTAC/osv-results-reporter
[osvtac]: https://osvtac.github.io/
