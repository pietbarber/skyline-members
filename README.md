skyline-members
===============

The members only section of the skyline website.
If you can stand looking at this code and not stab your eyes out with a rusty fork, you can find some ugly perl programs that we use on our members-only section of our website (skylinesoaring.org). 

There is so much improvement that can be made on this suite of programs.  In General:

1) Need to make the code lint-free.  I understand my programs have a handwriting problem -- the way i indent stuff drives other people crazy.  It's a habit I picked up in 10th grade, with learning Pascal.  I haven't been able to break it.  That was 1988. 
2) The way I always reference stuff without any sort of configuration files is pretty maddening. 
3) There are many times subroutines can be found copy-pasted and slightly modified to suit my needs in many programs. If I was a smart programmer, I'd set up some Perl Modules, and reference them many times, writing only once, and maintaining only one codebase. 
4) if I was a smarter programmer, I'd do this in Python and use something fancy like Django.  this wasn't really feasible since we were running an old ass version of RedHat until relatively recently.  Now that I'm running CentOS 6, we're actually using a modern version of Python that actually can run stuff off of the Internet. 
5) I really don't know much about writing data bases, so this database is kind of like the neanderthal's view of what a database should look like.  I see the cool things that postgres can do, and I can only poke a stick at it and grunt. 

