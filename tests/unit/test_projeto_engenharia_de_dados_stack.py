import json
import pytest

from aws_cdk import core
from projeto_engenharia_de_dados.projeto_engenharia_de_dados_stack import ProjetoEngenhariaDeDadosStack


def get_template():
    app = core.App()
    ProjetoEngenhariaDeDadosStack(app, "projeto-engenharia-de-dados")
    return json.dumps(app.synth().get_stack("projeto-engenharia-de-dados").template)


def test_sqs_queue_created():
    assert("AWS::SQS::Queue" in get_template())


def test_sns_topic_created():
    assert("AWS::SNS::Topic" in get_template())
