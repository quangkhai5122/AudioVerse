"""AudioVerse cash-flow unit economics illustration.

NOT a vendor quote or prediction. Currency USD except explicit VND labels.
Usage: python scripts/cost_model.py [--mau 3000 --paid-share 0.03 ...]
"""
import argparse
import json


def evaluate(mau: int, paid_share: float, fixed_audio_hours: float,
             generated_audio_hours: float, tts_usd_per_m_chars: float,
             llm_usd_per_hour: float, infra_usd: float,
             marketing_usd: float = 0, creator_fixed_usd: float = 0,
             price_vnd: int = 59000, fx_vnd_per_usd: float = 26000,
             app_fee_share: float = .15, royalty_post_store_share: float = .30,
             chars_per_audio_hour: int = 45000) -> dict:
    if any(v < 0 for v in (mau, paid_share, fixed_audio_hours, generated_audio_hours,
                            tts_usd_per_m_chars, llm_usd_per_hour, infra_usd,
                            marketing_usd, creator_fixed_usd, price_vnd)):
        raise ValueError("Nonnegative input required")
    if any(x > 1 for x in (paid_share, app_fee_share, royalty_post_store_share)) or fx_vnd_per_usd <= 0:
        raise ValueError("Invalid percentage or currency rate")
    payers = round(mau * paid_share)
    gross_usd = payers * price_vnd / fx_vnd_per_usd
    after_store = gross_usd * (1 - app_fee_share)
    after_royalty = after_store * (1 - royalty_post_store_share)
    rendered_hours = fixed_audio_hours + generated_audio_hours
    tts_usd = rendered_hours * chars_per_audio_hour / 1_000_000 * tts_usd_per_m_chars
    llm_usd = generated_audio_hours * llm_usd_per_hour
    variable_usd = tts_usd + llm_usd
    costs = variable_usd + infra_usd + marketing_usd + creator_fixed_usd
    return {
        "mau": mau, "payers": payers, "gross_usd": round(gross_usd, 2),
        "after_store_and_royalty_usd": round(after_royalty, 2),
        "tts_usd": round(tts_usd, 2), "llm_usd": round(llm_usd, 2),
        "infra_usd": infra_usd, "marketing_usd": marketing_usd,
        "creator_fixed_usd": creator_fixed_usd,
        "contribution_after_modeled_costs_usd": round(after_royalty - costs, 2),
        "note": "EXCLUDES tax, refunds, support staff, rights minimum guarantees not separately modeled, transaction chargebacks, paid AI for other workflows and amortization. Numbers are illustrative."
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--mau', type=int, default=3000)
    parser.add_argument('--paid-share', type=float, default=.03)
    parser.add_argument('--fixed-audio-hours', type=float, default=100)
    parser.add_argument('--generated-audio-hours', type=float, default=300)
    parser.add_argument('--tts-rate', type=float, default=16.5, help='USD / 1M characters')
    parser.add_argument('--llm-per-hour', type=float, default=.2604)
    parser.add_argument('--infra-usd', type=float, default=100)
    parser.add_argument('--marketing-usd', type=float, default=0)
    parser.add_argument('--creator-fixed-usd', type=float, default=0)
    parser.add_argument('--price-vnd', type=int, default=59000)
    args = parser.parse_args()
    print(json.dumps(evaluate(args.mau, args.paid_share, args.fixed_audio_hours,
        args.generated_audio_hours, args.tts_rate, args.llm_per_hour,
        args.infra_usd, args.marketing_usd, args.creator_fixed_usd,
        args.price_vnd), ensure_ascii=False, indent=2))


if __name__ == '__main__':
    main()
