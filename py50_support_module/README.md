# py50_streamlit_support

[py50 package](https://github.com/tlint101/py50) has recently been updated to version 1.0. This version allows the 
generation of basic statistical annotations to the plots. However, py50 is dependent on [Statannotations](https://github.com/trevismd/statannotations).
Unfortunately, at this time Statannotations is not compatible with Seaborn versions 0.12 or higher. This is unfortunate 
as the newer versions of Seaborn contains better control of the error bars. 

As the goal of this project was to annotate plots with statistics, this is unfortunate. During testing, it was 
discovered that py50 would not have issues with updates to Seaborn. However, during pip installation, this would output 
errors. Fortunately, errors can be skipped on the python installation. Unfortunately, this is not the case for the 
Streamlit web application.   

As a work around, some code for hte streamlit application has been modified to circumvent these issues and allow for the 
installation of the newer versions of Seaborn.

**Note:** These fixes are for the streamlit version only. For those interested in using py50 python code, please see the 
mian repository [here](https://github.com/tlint101/py50).

Install using the following:
```
pip install py50_streamlit_support
```

or:

```
pip install py50_streamlit_support -U
```