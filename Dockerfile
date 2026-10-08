# ARIA container image. Standard library only; the one package installed is the optional 7z reader for offline AutoSupport imports.
FROM python:3.12-slim

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    ARIA_BIND=0.0.0.0 \
    ARIA_PORT=8080 \
    ARIA_DATA_DIR=/var/lib/aria \
    ARIA_AUTH=local

RUN pip install --no-cache-dir py7zr==0.22.0 \
 && useradd --uid 10001 --create-home --shell /usr/sbin/nologin aria \
 && mkdir -p /app /var/lib/aria/data \
 && ln -s /var/lib/aria/data /app/data \
 && chown -R aria:aria /app /var/lib/aria

WORKDIR /app
COPY --chown=aria:aria server.py aria_auth.py perf_integration.py hw_docs_harvester.py api_queries.json resolution_rules.json version.json \
     index.html index_src.html app.js styles.css chart.js pptxgen.bundle.js /app/
COPY --chown=aria:aria tools/asup_parser.py tools/dqp_parser.py tools/firmware_harvester.py tools/reference_harvester.py tools/library_manager.py tools/ontap_release_notes.py tools/eoa_list.py tools/netapp_docs_versions.py /app/tools/
COPY --chown=aria:aria docker/entrypoint.sh /app/entrypoint.sh
RUN chmod +x /app/entrypoint.sh

USER 10001
VOLUME ["/var/lib/aria"]
EXPOSE 8080
HEALTHCHECK --interval=30s --timeout=5s --start-period=20s \
  CMD python -c "import urllib.request,os;urllib.request.urlopen('http://127.0.0.1:%s/healthz' % os.environ.get('ARIA_PORT','8080'),timeout=4)"
ENTRYPOINT ["/app/entrypoint.sh"]
