import logging
import os
import jdk

def install_jdk_if_needed():
    """
    Install a compatible JDK if `JAVA_HOME` environment variable is not found.
    """
    if 'JAVA_HOME' not in os.environ:
        version = '17'
        adalina_jre_file = os.path.join(jdk._JRE_DIR, 'adalina_jre_version.txt')
        install_new_jre = True
        if os.path.exists(adalina_jre_file):
            jre_path = open(adalina_jre_file, 'r').read().strip()
            if os.path.exists(jre_path):
                logging.info(f'JAVA_HOME not set but JRE already downloaded')
                os.environ['JAVA_HOME'] = jre_path
                install_new_jre = False

        if install_new_jre:
            logging.info('JAVA_HOME not set, installing JRE...')
            java_home = jdk.install(version, jre=True)
            os.environ['JAVA_HOME'] = java_home
            with open(adalina_jre_file, 'w') as f:
                f.write(java_home)

    logging.info(f'JAVA_HOME set to {os.environ.get("JAVA_HOME")}')