import json
import os
import subprocess
import pytest

@pytest.mark.eda
@pytest.mark.skip(reason="Test server doesn't set up account info required to run slurm")
def test_gcd_server_slurm(gcd_chip):
    '''Basic sc-server test: Run a local instance of a server, and build the GCD
       example using loopback network calls to that server.
       The server uses a slurm cluster to delegate job steps in this test.
    '''

    # Start running an sc-server instance.
    os.mkdir('local_server_work')
    srv_proc = subprocess.Popen(['sc-server',
                                 '-nfs_mount', './local_server_work',
                                 '-cluster', 'slurm',
                                 '-port', '8089'])

    # Ensure that klayout doesn't open its GUI after results are retrieved.
    os.environ['DISPLAY'] = ''

    # Create the temporary credentials file, and set the Chip to use it.
    tmp_creds = '.test_remote_cfg'
    with open(tmp_creds, 'w') as tmp_cred_file:
        tmp_cred_file.write(json.dumps({'address': 'localhost', 'port': 8089}))
    gcd_chip.set('remote', True)
    gcd_chip.set('credentials', os.path.abspath(tmp_creds))

    gcd_chip.run()

    # Kill the server process.
    srv_proc.kill()

    # Verify that GDS was generated and returned.
    assert os.path.isfile('build/gcd/job0/export/0/outputs/gcd.gds')

if __name__ == "__main__":
    from tests.fixtures import gcd_chip
    test_gcd_server_slurm(gcd_chip())
