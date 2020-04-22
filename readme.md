# Where.guru

The app that helps you find cool places

Where.guru is a specialized search engine focussed on places.

## Project Status

Where.guru is a research project based on the mamut.cool profiling and recommendation platform.
Where.guru is at a Minimal Viable Product stage, with a focus on restaurants in france
If you live in Paris, or even more if you are visiting Paris, you've got to check out [where.guru](http://where.guru)!!!

## Contributing to the Project

Where.guru app is still in its early stages and is looking for passionate developers, ux designers, data scientists, system engineers, online marketing gurus and community managers.
We believe it is a great opportunity for talented professionals to contribute to a cool project.
Please make sure you check our [Contributing Guidelines](doc/CONTRIBUTING.md) and [Code of Conduct ](doc/CODE_OF_CONDUCT.md)

Please do not hesitate to contact the [author](https://github.com/fmaine) if this project inspires you!

## Technologies

We like to keep the list short and simple
* The main programming language for the platform is **Python 3**
* Data are managed with **pandas dataframes**
* Web side based on  **HTML5**, **CSS3** and **JQuery**
* Dynamic data are handled server side with **flask** served by **gunicorn**
* where.guru is run on Ubuntu 18 + nginx + gunicorn
* Some notable dependencies :
  * Check `requirements.txt` file for extensive list of dependencies
* For development we enjoy using the coolest tools available :
  * [jupyter notebook](https://jupyter.org/)
  * [atom](https://www.atom.io)
  * and of course [Github](https://www.github.com)

## Directory Structure

* `python` : python sources
  * `api` : Web service and database code
  * `importers` : Data importers = Spiders + Importers
  * `db` : Database import, cleansing, curation and export
  * `misc` : Miscellaneous tools and utils
* `www` : Static web files - html, css, images, js...
* `doc` : documentation
* `data` : Database and datafiles
* `bin` : Executables
* `etc` : Config files
* `log` : Log files


Use of python 3 `virtualenv` is recommended is you want to install the package

## Authors

* **François Bancilhon** - *Advisor & Guru*
* **Thibault Taupin** - *UX & UI design* - [thibaulttaupin](https://github.com/thibaulttaupin)
* **François Maine** - *Initial work and Benevolent Dictatorship* - [fmaine](https://github.com/fmaine)

## License

This github repo is limited to the **open source version** of the platform, without the data science features and a subset of data sources.

This subset of the project is licensed under the MIT License - see the [LICENSE](doc/LICENSE) file for details

## Acknowledgments

* Hat tip to anyone whose code was used
