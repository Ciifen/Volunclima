#!/bin/bash
readonly envFile="/var/py/volunclima/scripts/prediccion/venv/bin/activate"
source ${envFile}
cd /var/py/volunclima/scripts/prediccion/
python3.9 generar.py
python3.9 prediccion.py
python3.9 prediccion_rango_fecha.py
sshpass -p ***** scp -P **** -o StrictHostKeyChecking=no /var/py/volunclima/salidas/predicciones/sudam/pron_tsaireECMWF_sudam_mens_anom.png host.com:/home/ciifenor/public_html/wp-content/uploads/imagenes_clima/pronostico/pron_tsaire/pron_tsaireECMWF_sudam_mens_anom.png
sshpass -p ***** scp -P **** -o StrictHostKeyChecking=no /var/py/volunclima/salidas/predicciones/sudam/pron_tsaireECMWF_sudam_mens.png  host.com:/home/ciifenor/public_html/wp-content/uploads/imagenes_clima/pronostico/pron_tsaire/pron_tsaireECMWF_sudam_mens.png
sshpass -p ***** scp -P **** -o StrictHostKeyChecking=no /var/py/volunclima/salidas/predicciones/sudam/pron_tsaireECMWF_sudam_estac_anom.png  host.com:/home/ciifenor/public_html/wp-content/uploads/imagenes_clima/pronostico/pron_tsaire/pron_tsaireECMWF_sudam_estac_anom.png
sshpass -p ***** scp -P **** -o StrictHostKeyChecking=no /var/py/volunclima/salidas/predicciones/sudam/pron_tsaireECMWF_sudam_estac.png  host.com:/home/ciifenor/public_html/wp-content/uploads/imagenes_clima/pronostico/pron_tsaire/pron_tsaireECMWF_sudam_estac.png

sshpass -p ***** scp -P **** -o StrictHostKeyChecking=no /var/py/volunclima/salidas/predicciones/sudam/pron_prcpECMWF_sudam_mens_anom.png host.com:/home/ciifenor/public_html/wp-content/uploads/imagenes_clima/pronostico/pron_precipitacion/pron_prcpECMWF_sudam_mens_anom.png
sshpass -p ***** scp -P **** -o StrictHostKeyChecking=no /var/py/volunclima/salidas/predicciones/sudam/pron_prcpECMWF_sudam_mens.png  host.com:/home/ciifenor/public_html/wp-content/uploads/imagenes_clima/pronostico/pron_precipitacion/pron_prcpECMWF_sudam_mens.png
sshpass -p ***** scp -P **** -o StrictHostKeyChecking=no /var/py/volunclima/salidas/predicciones/sudam/pron_prcpECMWF_sudam_estac_anom.png  host.com:/home/ciifenor/public_html/wp-content/uploads/imagenes_clima/pronostico/pron_precipitacion/pron_prcpECMWF_sudam_estac_anom.png
sshpass -p ***** scp -P **** -o StrictHostKeyChecking=no /var/py/volunclima/salidas/predicciones/sudam/pron_prcpECMWF_sudam_estac.png  host.com:/home/ciifenor/public_html/wp-content/uploads/imagenes_clima/pronostico/pron_precipitacion/pron_prcpECMWF_sudam_estac.png
sshpass -p ***** scp -P **** -o StrictHostKeyChecking=no /var/py/volunclima/salidas/predicciones/pacec/pron_prcpECMWF_pacec_mens_anom.png host.com:/home/ciifenor/public_html/wp-content/uploads/imagenes_clima/pronostico/pron_precipitacion/pron_prcpECMWF_pacec_mens_anom.png
sshpass -p ***** scp -P **** -o StrictHostKeyChecking=no /var/py/volunclima/salidas/predicciones/pacec/pron_prcpECMWF_pacec_mens.png  host.com:/home/ciifenor/public_html/wp-content/uploads/imagenes_clima/pronostico/pron_precipitacion/pron_prcpECMWF_pacec_mens.png
sshpass -p ***** scp -P **** -o StrictHostKeyChecking=no /var/py/volunclima/salidas/predicciones/pacec/pron_prcpECMWF_pacec_estac_anom.png  host.com:/home/ciifenor/public_html/wp-content/uploads/imagenes_clima/pronostico/pron_precipitacion/pron_prcpECMWF_pacec_estac_anom.png
sshpass -p ***** scp -P **** -o StrictHostKeyChecking=no /var/py/volunclima/salidas/predicciones/pacec/pron_prcpECMWF_pacec_estac.png  host.com:/home/ciifenor/public_html/wp-content/uploads/imagenes_clima/pronostico/pron_precipitacion/pron_prcpECMWF_pacec_estac.png