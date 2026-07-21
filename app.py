from flask import Flask, render_template, request

app = Flask(__name__)

# ==============================
# SETTINGS
# ==============================
LOW_RATE = 0.2703
HIGH_RATE = 0.3703
OFF_PEAK_MULTIPLIER = 0.8
PEAK_MULTIPLIER = 1.2
AVG_POWER = 1.5


# ==============================
# BILL CALCULATION
# ==============================
def calculate_bill(off, peak, days):
    off_kwh = off * AVG_POWER * days
    peak_kwh = peak * AVG_POWER * days
    total_kwh = off_kwh + peak_kwh

    rate = LOW_RATE if total_kwh <= 1500 else HIGH_RATE

    off_cost = off_kwh * rate * OFF_PEAK_MULTIPLIER
    peak_cost = peak_kwh * rate * PEAK_MULTIPLIER

    total_cost = off_cost + peak_cost

    extra = 0 if total_kwh <= 600 else 10

    return total_kwh, total_cost + extra


# ==============================
# OPTIMIZATION
# ==============================
def optimize_usage(off, peak):
    shift = peak * 0.3
    return off + shift, peak - shift


# ==============================
# ROUTES
# ==============================
@app.route('/')
def home():
    return render_template('index.html')


@app.route('/predict', methods=['POST'])
def predict():
    try:
        off = float(request.form['off_peak'])
        peak = float(request.form['peak'])
        days = int(request.form['days'])

        if off < 0 or peak < 0:
            return render_template('index.html', error="Hours cannot be negative")

        if off + peak > 24:
            return render_template('index.html', error="Total hours cannot exceed 24")

        if days <= 0 or days > 31:
            return render_template('index.html', error="Days must be 1–31")

        # Current
        kwh, monthly = calculate_bill(off, peak, days)
        next_month = monthly * 1.05

        # Optimized
        new_off, new_peak = optimize_usage(off, peak)
        _, optimized = calculate_bill(new_off, new_peak, days)
        savings = monthly - optimized

        # Usage level
        if monthly > 300:
            usage_level = "High ⚠️"
        elif monthly > 150:
            usage_level = "Medium"
        else:
            usage_level = "Low ✅"

        # Suggestion
        if savings > 0:
            recommendation = f"💡 You can save RM {round(savings,2)} by shifting usage to off-peak hours."
        else:
            recommendation = "✅ Your usage is already efficient."

        return render_template(
            'index.html',
            kwh=round(kwh,2),
            monthly=round(monthly,2),
            next_month=round(next_month,2),
            optimized=round(optimized,2),
            savings=round(savings,2),
            usage_level=usage_level,
            recommendation=recommendation
        )

    except Exception as e:
        return render_template('index.html', error=str(e))


if __name__ == "__main__":
    app.run(debug=True)