FROM mcr.microsoft.com/windows/servercore:20H2

RUN @"%SystemRoot%\System32\WindowsPowerShell\v1.0\powershell.exe" -NoProfile -InputFormat None -ExecutionPolicy Bypass -Command " [System.Net.ServicePointManager]::SecurityProtocol = 3072; iex ((New-Object System.Net.WebClient).DownloadString('https://chocolatey.org/install.ps1'))" && SET "PATH=%PATH%;%ALLUSERSPROFILE%\chocolatey\bin"
RUN choco install -y python3
RUN set PATH=%PATH%;C:\python39
RUN set PATH=%PATH%;C:\python39\Scripts

ARG CACHEBUST
RUN pip install nanome

ENV ARGS=''

COPY . /app
WORKDIR /app

CMD python run.py %ARGS%