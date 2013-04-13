README dvm-dos-tem EXTRAPOLATION VERSION
===========================================
The dvm-dos-tem is a process based bio-geo-chemical ecosystem model.

More info...?

Downloading
-------------
There are several options for downloading or obtaining the model depending on your 
particular usecase. Dvm-dos-tem is not distributed as a binary file, so you must compile 
from source code. 

* If you anticipate contributing to the code, you should use github to create
your own fork and then git to "clone" the code.
* How to: ...download version, keep up to date with sel version...
* How to: ...download specific commit, no need to contribute or keep up to date...

Compiling / Building
-----------------------
This project requires a version of NetCDF and Boost's program options to be installed on 
your path. Assuming both of those exist, this should work to compile:

    $ make

or 

    $ make dvm
    
There are some helpful scripts provided in the `env-setup-scripts/` folder that will set 
a few environment variables for you for specific systems. For instance on aeshna, the 
correct version of NetCDF is not provided as a system package, but the user tobey has
made it available so that you don't have to compile it yourself. You must set an
environment variable so that when you compile and run it will look in tobey's directory 
for the NetCDF library files.

You can either remember to run the setup commands/script each time you logon to the 
computer where are you are interacting with the model or add a line to your ~/.bashrc 
or ~/.bash_profile that "sources" the setup script. This makes sure the setup commands
are run each time you log on. 
E.g.

    $ vim ~/.bash_profile
    # Add a line like this at the end:
    source /path/to/your/dvm-dos-tem/env-setup-scripts/setup-env-for-aeshna.sh
    
If you are successful getting dvm-dos-tem to compile and run on a different system
it would be appreciated if you submit the appropriate setup commands so that other's
don't have to spend time figuring out those details.

Running
---------
The program is partially controlled by a set of command line options. The `--help`
provides some info and shows the defaults:

    $ ./DVMDOSTEM --help
      -m [ --mode ] arg (=siterun)          change mode between siterun and regnrun
      -f [ --control-file ] arg (=config/controlfile_site.txt)
                                            choose a control file to use
      -c [ --cohort-id ] arg (=1)           choose a specific cohort to run
      -s [ --space-time-config ] arg        choose spatial or temporal running mode
      -h [ --help ]                         produces helps message
      -v [ --version ]                      show the version information
      -d [ --debug ]                        enable debug mode

The DATA/ directory of this project contains some sample data for single site runs and 
some multi-site runs (multiple grid cells or cohorts). To use the default values, simply
run the program like this:

    $ ./DVMDOSTEM


Developing
-----------
This project is maintained using Git (an open source distributed version control system) 
and github (a web service that provides hosting for code projects and has tools and idioms
for collaborative working on code-related projects.

This project is maintained using the "Fork and Pull" workflow. Following are several 
common use-cases:

* To simply download and use a certain version of the software, no special tools or 
programs are necessary.
    
    Navigate to the project's "Code" view on github, select the branch or tag of the code
    to get and use the download link.

* If you plan to make changes to the source code that should be incorporated into the 
Spatial Ecology Lab's main repository, then you will need the program Git on your
computer. 

Git is, at heart, a command line tool, but there are numerous graphic front-ends (GUIs)
available for Mac, Windows and Linux. If you are using SEL's aeshna cluster, Git is 
already installed along with two helpful graphical tools, gitk and git-gui. There are 
Git plugins for many other software development tools as well (e.g. Eclipse). Using the
graphical tools may be easier if you have a basic familiarity with using Git from the
command line.

Here are two resources for getting and installing git on your computer:

* Github, how to setup Git <https://help.github.com/articles/set-up-git>
* Git Book, installing git <http://git-scm.com/book/en/Getting-Started-Installing-Git>

In general, the Git Book <http://git-scm.com/book/en/> is a good reference.

Then you will need to follow the ideas described here to be able to keep your code
up-to-date and to be able to contribute changes: <https://help.github.com/articles/fork-a-repo>.

After installing git on your computer and downloading the source code, here are a number 
of settings, configurations, and "tweaks" that may be helpful for working with Git and 
github.

* Maybe start with this (Git Book again): <http://git-scm.com/book/en/Customizing-Git-Git-Configuration>.
    
    The settings concerning pager, external editors, and color are particularly useful.

* Install and use gitk and git-gui (These come default with most installations of Git).
    
    * Gitk is a history viewer
    * Git Gui allows you to add changes and commit them to the repository.

* It is helpful if the prompt in your terminal program displays which branch you currently
have checked out when you enter a directory with a git repository. To do this, you add a
function to your `.bashrc` file. The `.bashrc` file is a setting file that is present in
every user's home directory on most Linux like computers. The '.' in the file name makes
the file "hidden"; use `ls -a` to see the file. If it is not present in your directory,
you can create it. Add this to your `.bashrc` file:

        \# function to find the current git branch
        function parse_git_branch {
            git branch --no-color 2> /dev/null | sed -e '/^[^*]/d' -e 's/* \(.*\)/[\1] /'
        }
        
        \# use parse_git_branch to add the git branch to your terminal prompt
        PS1=$PS1: $(parse_git_branch)

**NOTE:** You have to remember to reload the `.bashrc` file, either by closing and
re-opening your terminal window, or typing:

    $ source ~/.bashrc


### Workflow

For starters we will try the "integration manager" workflow. This is what is described
[here](https://help.github.com/articles/fork-a-repo). This means that to get started you
should first "fork" the project from the github.com/ua-snap/dvm-dos-tem.git repository. 
This will give you your own dvm-dos-tem repository in your own github account 
(github.com/YOU/dvm-dos-tem.git). Next you will "clone" from your account to your own 
machine (where ever you perform your coding work). Finally when you have made changes on 
your own working machine you will "push" those changes back to _your_ fork. If you would 
like the changes you made to be incorporated into the shared project
(github.com/ua-snap/dvm-dos-tem.git), then issue a "pull request" from your github 
account.

Documentation
-------------
There is a Doxygen file (Doxyfile) included with this project. The current settings are
for the Doxygen output to be generated in the docs/dvm-dos-tem/ directory.

The file is setup to build a very comprehensive set of documents, including as many 
diagrams as possible (call graphs, dependency diagrams, etc). To build the diagrams, 
Doxygen requires a few extra packages, such as the dot package. This is not available on 
aeshna, so running Doxygen on aeshna will produce a bunch of errors.