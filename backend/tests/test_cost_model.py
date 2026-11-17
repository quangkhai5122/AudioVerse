import importlib.util
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]


def load_model():
    path=ROOT/'scripts/cost_model.py'
    spec=importlib.util.spec_from_file_location('cost_model',str(path))
    module=importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module.evaluate


def test_cost_zero_demand():
    evaluate=load_model()
    value=evaluate(mau=0,paid_share=0,fixed_audio_hours=0,generated_audio_hours=0,
                   tts_usd_per_m_chars=16.5,llm_usd_per_hour=.2604,infra_usd=0)
    assert value['gross_usd']==0
    assert value['tts_usd']==0
    assert value['contribution_after_modeled_costs_usd']==0


def test_cost_one_hour_audio():
    evaluate=load_model()
    value=evaluate(mau=0,paid_share=0,fixed_audio_hours=1,generated_audio_hours=0,
                   tts_usd_per_m_chars=16.5,llm_usd_per_hour=.2604,infra_usd=0)
    assert value['tts_usd']==pytest.approx(.74,abs=.01)


def test_invalid_paid_share_is_rejected():
    evaluate=load_model()
    with pytest.raises(ValueError):
        evaluate(100,1.5,1,0,16.5,.26,20)
