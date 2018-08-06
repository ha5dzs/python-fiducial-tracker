# Frequently asked questions
FAQ goes here, I will fill it up as the questions come in.

## Q: Why don't you use better algorithms? You could have used SIFT instead of ORB for feature matching, and SolvePnPRansac instead of SolvePNP
I tried them, and they crashed for me. I am not sure why did this happen, it might well be because I used a Mac, or because I have something wrong with my Python environment, which I got entirely using Homebrew.

## Q: Sometimes the code just fails instead of initialising the camera. Any remedies?
I think this happens because the camera is not released properly by the previous instance of Python. Try making sure that the camera is not initialised before starting the code.

## Q: I am getting error messages that are very vague. Why?
There is very little sanity check and error management built-in the code. For instance, when a section is missing from the config file, ConfigParser will fail. If you look carefully, you might find out why. But then again, this is not production-quality code, I developed this to develop something else for the research lab I am working in.

## Q: I have a feature request. Can you implement -insert random weird function here- for me?
I am afraid, this was a side project for me. I have some science to do over here, so I can't really afford to be a pocket software developer. However, if it's something simple, it may be done. Or better yet, somebody might actually contribute to this thing! Try opening an issue, and see where it goes.

## Q: I am trying to get your code on a different platform, but it doesn't seem to work. What can you do?
I only had two computers to try this code with. One was a mac, and the other was an old computer with Linux on it. On Linux, `imhow()` didn't seem to work for me. It seemed to be an issue with some C-code in the OpenCV package, and I couldn't really spare the time to figure it all out. Nevertheless, the Python code should be pretty much platform-independent, and I am using 'stock' modules as much as possible.

## Q: Your code is ugly. What were you thinking?
Well, thanks :)  
I wrote this while recovering from an operation. I did have to take a lot of very strong painkillers, most of them were opiates. So there you go, I wrote ugly code because I was high on drugs. What's your excuse?
