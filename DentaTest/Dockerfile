FROM mcr.microsoft.com/dotnet/core/aspnet:3.0
WORKDIR '/app'

RUN apt-get -y update && apt-get install --no-install-recommends -y \
                            software-properties-common
RUN apt-add-repository contrib

RUN echo ttf-mscorefonts-installer msttcorefonts/accepted-mscorefonts-eula select true | \
    debconf-set-selections

RUN apt-get update && apt-get install --no-install-recommends -y \
                        libgdiplus \
                        ttf-mscorefonts-installer

COPY DentaTest/bin/Release/netcoreapp3.0/publish  /app/
CMD /app/DentaTest

