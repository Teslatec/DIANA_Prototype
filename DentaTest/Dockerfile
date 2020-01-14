FROM mcr.microsoft.com/dotnet/core/sdk:3.0 AS builder
WORKDIR '/src'
COPY DentaTest /src/DentaTest/
COPY DentaTest.sln /src/
RUN dotnet add DentaTest package Drive.MigraDocPdfSharp --version 1.0.0-preview2-1
RUN dotnet publish -c Release

FROM mcr.microsoft.com/dotnet/core/aspnet:3.0
WORKDIR '/app'

RUN apt-get -y update && apt-get install --no-install-recommends -y \
                            software-properties-common
RUN apt-add-repository contrib

RUN echo ttf-mscorefonts-installer msttcorefonts/accepted-mscorefonts-eula select true | \
    debconf-set-selections

RUN apt-get update && apt-get install --no-install-recommends -y \
                        libgdiplus \
                        ttf-mscorefonts-installer \
                        fonts-crosextra-carlito \
                        fonts-crosextra-caladea

COPY logo.png /app/
COPY --from=builder /src/DentaTest/bin/Release/netcoreapp3.0/publish /app/
CMD /app/DentaTest

