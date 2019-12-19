FROM mcr.microsoft.com/dotnet/core/aspnet:3.0
WORKDIR '/app'
RUN apt-get update && apt-get install --no-install-recommends -y \
                        libgdiplus
COPY DentaTest/bin/Release/netcoreapp3.0/publish  /app/
CMD /app/DentaTest

