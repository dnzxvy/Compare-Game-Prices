from flask import Flask, render_template, request
import csv

app = Flask(__name__)


def parse_price(price_str):
    try:
        if price_str.lower() == 'free':
            return 0.0
        return float(price_str.replace('£', '').replace(',', '').strip())
    except ValueError:
        return float('inf')


def get_all_games():
    results = []
    with open('ps5games.csv', 'r', encoding='utf-8') as file:
        reader = csv.DictReader(file)
        for row in reader:
            results.append(row)
    return results


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/ps5_games')
@app.route('/ps5_games/page/<int:page>')
def ps5_games(page=1):
    results_per_page = 25
    results = get_all_games()

    sort_option = request.args.get('sort', 'low-to-high')
    # Sort results
    if sort_option == 'high-to-low':
        results.sort(key=lambda x: parse_price(x['Price']), reverse=True)
    else:
        results.sort(key=lambda x: parse_price(x['Price']))

    total_pages = len(results) // results_per_page + (1 if len(results) % results_per_page > 0 else 0)

    start = (page - 1) * results_per_page
    end = start + results_per_page
    paginated_results = results[start:end]

    return render_template('ps5_games.html', results=paginated_results, all_games=results, page=page,
                           total_pages=total_pages)


if __name__ == '__main__':
    app.run(debug=True)
