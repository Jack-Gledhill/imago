# =====================
# Import PATH libraries
# =====================
# -----------------
# Builtin libraries
# -----------------
from os import _exit
from typing import Optional, Any
from sys import _getframe
from datetime import datetime

# ---------------------
# Third-party libraries
# ---------------------
from termcolor import colored

# ======================
# Import local libraries
# ======================
from .blueprints import log, timestamp

LOG_FORMAT = "{ts.day}-{ts.month}-{ts.year} {ts.hour}:{ts.minute}:{ts.second}:{ts.microsecond} {level}  [{project}:{origin}]: {content}"
ORIGIN_FORMAT = "{file_name}.{func_name}"

class Custos:
    """This is a device used to easily print coloured text to the stdout without the need for messy code.
    
    It also allows for a more authentic printing method if an instance of this class is assigned to a "console" variable, examples of how this would look are:
        console.info(text="Successfully started up!")
        
        try:
            ...
            
        except:
            console.warn(text="Something failed!")
            
    Options and how to define them
    ==============================
    
    Several options can be provided to this class to change the way it works.
    
    To set options, simply pass the option name as a keyword argument along with the value you wish to set. For example:
        Custos(option=value)
        
    Log & Prompt Format
    -------------------

    Sometimes, people may wish to change the format of the information that gets logged to the console. Luckily, this is pretty easy to do with Custos.

    Due to the way Python string interpolation (formatted strings) works, we can't use .strftime inside of format strings. This means that you can't change the datetime formatting listed below.
    Luckily, we can just use different variables for each of the time units of the datetime.

    You can change the log format by doing something similar to this:
        Custos(log_format="[{ts.day}-{ts.month}-{ts.year}] {level}  [{project}.{origin}] >> {content}")

    To set the format of prompt calls, simply do something like this:
        Custos(prompt_format="[{ts.day}-{ts.month}-{ts.year}] {level}  [{project}.{origin}]: {content} >>")

    The prompt format has the same available variables as the log format does.

    Below is a list of available variables that you can put into your format string:
        ts - the timestamp of the log containing these values:
            year - the year that the log was created
            month - the zero padded month that the log was created
            day - the zero padded day of the month that the log was created

            hour - the zero padded hour of the day that the log was created
            minute - the zero padded minute of the hour that the log was created
            second - the zero padded second of the minute that the log was created
            microsecond - the decimal value of the microsecond of the second that the log was created

            hour_12 - the 12-hour clock value of the hour of the day that the log was created
            am_pm - AM or PM depending on the time of day

        project - the optional name of the project (defaults to custos)

        id - the ID of the log
        level - the urgency level of the log, e.g: info

        origin - the provided or queried origin of the call
        content - the content of the log

    [Note]: The provided format should be a partially formatted string that uses the {} syntax.

    Origin Format
    -------------

    You can also specify a format for the origin of the log. This works similarly to the log and prompt formats, except it's set using:
        Custos(origin_format="{file_name}.{func_name}#{line_no}")

    Here are the possible variables you can provide:
        file_name - the optional name of the file that the call came from (defaults to "module")
        func_name - the optional name of the function containing the call (defaults to "external")
        line_no - the line number at which the call was made

    Logging level
    -------------
    
    This wouldn't be a proper logging handler without a logging level. In essence, the value of this option determines which type of logs are able to be printed to the console.
    
    Log levels run on a hierarchy system, if verbose logs can be printed, so can info, warning, error (etc.) logs. If the logging level is set to warning, then info and verbose will not be printed etc.

    To set a log level, you can do something like this:
        Custos(log_level="warning")

    The possible values for this option are as follows:
        verbose: every log is printed
        info: info logs and logs listed below are printed
        ready: ready logs and logs listed below are printed
        warn: warning logs and logs listed below are printed
        error: error logs and logs listed below are printed
        critical: critical logs and logs listed below are printed
        fatal: only fatal logs are printed

    [Note]: Regardless of log level, every log will be available in the Custos.logs list, they just aren't printed to the stdout.
    
    Project name
    ------------
    
    This logging system prints an origin with every log made. It looks like this:
        [custos:origin_function]
        
    However, you can swap custos for whatever word you want by passing the project_name value, below is an example:
        Custos(project_name="dominus")
        
    [Note]: As long as the value for this option can be turned into a string, the module doesn't care about what the type of the value is.
    
    Using multiple consoles
    =======================
    
    Since this module allows you to choose project names for your logger, you could theoretically have different instances of this class with different project names.
    This would allow you to provide more clarity on the source of your logs. For example:
        master_console = Custos(project_name="master",
                                log_level="verbose")
                                
        slave_console = Custos(project_name="slave",
                               log_level="error")"""
    
    def __init__(self,
                 **options: dict):
        self.log_level: Optional[str] = options.pop("log_level", "info")
        self.project_name: Optional[str] = options.pop("project_name", "custos")

        self.format: str = options.pop("log_format", LOG_FORMAT)
        self.prompt_format: str = options.pop("prompt_format", self.format + " >> ")

        self.origin_format: str = options.pop("origin_format", ORIGIN_FORMAT)

        self.logs = []

    def get_origin(self,
                   depth: Optional[int] = 2) -> str:
        """Returns the formatted version of the origin with an optional depth.
        
        The depth determines which function to get the frame for, a depth of two returns the origin
        if called from one of this class' functions. If called externally, you should pass depth as 1.
        
        Thanks to how Python works, it's not actually possible for the frame to be missing the f_code property, so there's no need to check for that."""

        frame = _getframe(depth)
        file_name = frame.f_code.co_filename.split("/")[-1][:-3]
        func_name = frame.f_code.co_name

        return self.origin_format.format(file_name="module" if file_name == "<module>" else file_name,
                                         func_name=func_name if func_name else "external",
                                         line_no=frame.f_lineno)

    def fatal(self,
              text: str,
              origin: Optional[str] = None):
        """This creates a fatal message and prints it to the stdout.
        
        This is designed to be used whenever the project has decided to initiate a controlled shutdown."""

        if origin is None:
            origin = self.get_origin()

        now = datetime.utcnow()

        self.logs.append(log(project=self.project_name,
                             timestamp=now,
                             format_string=self.format,

                             log_level="fatal",
                             log_id=len(self.logs) + 1,

                             origin=origin,
                             content=text))

        if self.log_level not in ("verbose", "info", "ready", 
                                  "warning", "error", "critical", 
                                  "fatal"):
            return

        print(self.format.format(ts=timestamp(object=now),
                                 level=colored(text="fatal   ", 
                                               color="red"),

                                 project=colored(text=self.project_name,
                                                 color="green"),
                                 id=len(self.logs) + 1,

                                 origin=colored(text=origin,
                                                color="blue"),
                                 content=text))

    def critical(self, 
                 text: str,
                 origin: Optional[str] = None):
        """This creates a critical message and prints it to the stdout.
        
        This should be used in the event that something very dangerous happens in the application but doesn't warrant a shutdown."""

        if origin is None:
            origin = self.get_origin()

        now = datetime.utcnow()

        self.logs.append(log(project=self.project_name,
                             timestamp=now,
                             format_string=self.format,

                             log_level="critical",
                             log_id=len(self.logs) + 1,

                             origin=origin,
                             content=text))

        if self.log_level not in ("verbose", "info", "ready", 
                                  "warning", "error", "critical"):
            return

        print(self.format.format(ts=timestamp(object=now),
                                 level=colored(text="critical", 
                                               color="red"),

                                 project=colored(text=self.project_name,
                                                 color="green"),
                                 id=len(self.logs) + 1,

                                 origin=colored(text=origin,
                                                color="blue"),
                                 content=text))

    def error(self, 
              text: str,
              origin: Optional[str] = None):
        """This creates a error message and prints it to the stdout.
        
        This should be used when an unhandled error occurs in the application."""

        if origin is None:
            origin = self.get_origin()

        now = datetime.utcnow()

        self.logs.append(log(project=self.project_name,
                             timestamp=now,
                             format_string=self.format,

                             log_level="error",
                             log_id=len(self.logs) + 1,

                             origin=origin,
                             content=text))

        if self.log_level not in ("verbose", "info", "ready", 
                                  "warning", "error"):
            return

        print(self.format.format(ts=timestamp(object=now),
                                 level=colored(text="error   ", 
                                               color="red"),

                                 project=colored(text=self.project_name,
                                                 color="green"),
                                 id=len(self.logs) + 1,

                                 origin=colored(text=origin,
                                                color="blue"),
                                 content=text))

    def warn(self, 
             text: str,
             origin: Optional[str] = None):
        """This creates a warning message and prints it to the stdout.
        
        This is intended to be used when the application needs to make a clear notice to the maintainers that something went wrong."""

        if origin is None:
            origin = self.get_origin()

        now = datetime.utcnow()

        self.logs.append(log(project=self.project_name,
                             timestamp=now,
                             format_string=self.format,

                             log_level="warning",
                             log_id=len(self.logs) + 1,

                             origin=origin,
                             content=text))

        if self.log_level not in ("verbose", "info", "ready", 
                                  "warning"):
            return

        print(self.format.format(ts=timestamp(object=now),
                                 level=colored(text="warning ", 
                                               color="yellow"),

                                 project=colored(text=self.project_name,
                                                 color="green"),
                                 id=len(self.logs) + 1,

                                 origin=colored(text=origin,
                                                color="blue"),
                                 content=text))

    def info(self, 
             text: str,
             origin: Optional[str] = None):
        """This creates a info message and prints it to the stdout.
        
        This should be used when the application wants to make a log of something significant tht happened."""

        if origin is None:
            origin = self.get_origin()

        now = datetime.utcnow()

        self.logs.append(log(project=self.project_name,
                             timestamp=now,
                             format_string=self.format,

                             log_level="info",
                             log_id=len(self.logs) + 1,

                             origin=origin,
                             content=text))

        if self.log_level not in ("verbose", "info"):
            return

        print(self.format.format(ts=timestamp(object=now),
                                 level=colored(text="info    ", 
                                               color="cyan"),

                                 project=colored(text=self.project_name,
                                                 color="green"),
                                 id=len(self.logs) + 1,

                                 origin=colored(text=origin,
                                                color="blue"),
                                 content=text))

    def ready(self,
              text: str,
              origin: Optional[str] = None):
        """This creates a ready message and prints it to the stdout.
        
        This should be used when the application or one of its services becomes ready."""

        if origin is None:
            origin = self.get_origin()

        now = datetime.utcnow()

        self.logs.append(log(project=self.project_name,
                             timestamp=now,
                             format_string=self.format,

                             log_level="ready",
                             log_id=len(self.logs) + 1,

                             origin=origin,
                             content=text))

        if self.log_level not in ("verbose", "info", "ready"):
            return

        print(self.format.format(ts=timestamp(object=now),
                                 level=colored(text="ready   ", 
                                               color="green"),

                                 project=colored(text=self.project_name,
                                                 color="green"),
                                 id=len(self.logs) + 1,

                                 origin=colored(text=origin,
                                                color="blue"),
                                 content=text))

    def verbose(self, 
                text: str,
                origin: Optional[str] = None):
        """This creates a verbose message and prints it to the stdout.
        
        This can be used any time the application has absolutely anything to report to the maintainers, even if it's the tiniest thing."""

        if origin is None:
            origin = self.get_origin()

        now = datetime.utcnow()

        self.logs.append(log(project=self.project_name,
                             timestamp=now,
                             format_string=self.format,

                             log_level="verbose",
                             log_id=len(self.logs) + 1,

                             origin=origin,
                             content=text))

        if self.log_level != "verbose":
            return

        print(self.format.format(ts=timestamp(object=now),
                                 level=colored(text="verbose ", 
                                               color="magenta"),

                                 project=colored(text=self.project_name,
                                                 color="green"),
                                 id=len(self.logs) + 1,

                                 origin=colored(text=origin,
                                                color="blue"),
                                 content=text))

    def prompt(self,
               text: str,
               origin: Optional[str] = None):
        """This creates a PROMPT message and doesn't return until an input is given."""

        if origin is None:
            origin = self.get_origin()

        now = datetime.utcnow()

        self.logs.append(log(project=self.project_name,
                             timestamp=now,
                             format_string=self.format,

                             log_level="PROMPT",
                             log_id=len(self.logs) + 1,

                             origin=origin,
                             content=text))

        return input(self.prompt_format.format(ts=timestamp(object=now),
                                               level=colored(text="PROMPT  ", 
                                                             color="blue"),

                                               project=colored(text=self.project_name,
                                                               color="green"),
                                               id=len(self.logs) + 1,

                                               origin=colored(text=origin,
                                                              color="blue"),
                                               content=text))