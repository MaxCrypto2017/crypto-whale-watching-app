# Don't forget, if you find this useful please send ETH donations to: 0xc8a12868f79A5d77530E91247FEC84497890e572
# modules

# dash-related for app itself
import dash
from dash.dependencies import Output, Event
import dash_core_components as dcc
import dash_html_components as html

# non-dash-related libraries
import plotly.graph_objs as go
import pandas as pd
import gdax
import numpy as np

public_client = gdax.PublicClient()  # defines public client for all functions; taken from GDAX

# function to get data from GDAX to be referenced in our call-back later
def get_data():
    order_book = public_client.get_product_order_book('ETH-USD', level=3)
    ask_tbl = pd.DataFrame(data=order_book['asks'], columns=['price', 'volume', 'address'])
    bid_tbl = pd.DataFrame(data=order_book['bids'], columns=['price', 'volume', 'address'])

    # building subsetted table for ask data only
    # sell side (would be Magma)
    ask_tbl['price'] = pd.to_numeric(ask_tbl['price'])
    ask_tbl['volume'] = pd.to_numeric(ask_tbl['volume'])
    first_ask = float(ask_tbl.iloc[1, 0])
    perc_above_first_ask = (1.025 * first_ask)
    ask_tbl = ask_tbl[(ask_tbl['price'] <= perc_above_first_ask)]
    ask_tbl['color'] = 'red'

    # building subsetted table for bid data only
    # buy side (would be Viridis)
    bid_tbl['price'] = pd.to_numeric(bid_tbl['price'])
    bid_tbl['volume'] = pd.to_numeric(bid_tbl['volume'])
    first_bid = float(bid_tbl.iloc[1, 0])
    perc_above_first_bid = (0.975 * first_bid)
    bid_tbl = bid_tbl[(bid_tbl['price'] >= perc_above_first_bid)]
    bid_tbl['color'] = 'green'

    # flip the bid table
    bid_tbl = bid_tbl.iloc[::-1]

    # append the buy and sell side tables to create one cohesive view
    fulltbl = bid_tbl.append(ask_tbl)
    # limit our view to only orders greater than or equal to 1 ETH in size
    fulltbl = fulltbl[(fulltbl['volume'] >= 1)]

    # takes the square root of the volume (to be used later on for the purpose of sizing the orders
    fulltbl['sqrt'] = np.sqrt(fulltbl['volume'])

    final_tbl = fulltbl.groupby(['price'])[['volume']].sum()
    final_tbl['n_unique_orders'] = fulltbl.groupby('price').address.nunique().astype(float)
    final_tbl['price'] = final_tbl.index
    final_tbl['sqrt'] = np.sqrt(final_tbl['volume'])
    # making the tooltip
    final_tbl['text'] = ("There are " + final_tbl['volume'].map(str) + " ETH available for $" + final_tbl['price'].map(str) + " being offered by " + final_tbl['n_unique_orders'].map(str) + " ETH addresses")

    # get market price
    mp = public_client.get_product_ticker(product_id='ETH-USD')
    final_tbl['market price'] = mp['price']

    # makes the type float so that the next logical comparison can take place
    final_tbl['market price'] = final_tbl['market price'].astype(float)

    # determine buys / sells relative to last market price
    final_tbl['color'] = np.where(final_tbl['price'] > final_tbl['market price'], 'red', 'green')

    return final_tbl


######ETH-BTC#######
def get_data_ethbtc():
    order_book = public_client.get_product_order_book('ETH-BTC', level=3)
    ask_tbl = pd.DataFrame(data=order_book['asks'], columns=['price', 'volume', 'address'])
    bid_tbl = pd.DataFrame(data=order_book['bids'], columns=['price', 'volume', 'address'])

    # building subsetted table for ask data only
    # sell side (would be Magma)
    ask_tbl['price'] = pd.to_numeric(ask_tbl['price'])
    ask_tbl['volume'] = pd.to_numeric(ask_tbl['volume'])
    first_ask = float(ask_tbl.iloc[1, 0])
    perc_above_first_ask = (1.025 * first_ask)
    ask_tbl = ask_tbl[(ask_tbl['price'] <= perc_above_first_ask)]
    ask_tbl['color'] = 'red'

    # building subsetted table for bid data only
    # buy side (would be Viridis)
    bid_tbl['price'] = pd.to_numeric(bid_tbl['price'])
    bid_tbl['volume'] = pd.to_numeric(bid_tbl['volume'])
    first_bid = float(bid_tbl.iloc[1, 0])
    perc_above_first_bid = (0.975 * first_bid)
    bid_tbl = bid_tbl[(bid_tbl['price'] >= perc_above_first_bid)]
    bid_tbl['color'] = 'green'

    # flip the bid table
    bid_tbl = bid_tbl.iloc[::-1]

    # append the buy and sell side tables to create one cohesive view
    fulltbl = bid_tbl.append(ask_tbl)
    # limit our view to only orders greater than or equal to 1 ETH in size
    fulltbl = fulltbl[(fulltbl['volume'] >= 1)]

    # takes the square root of the volume (to be used later on for the purpose of sizing the orders
    fulltbl['sqrt'] = np.sqrt(fulltbl['volume'])

    final_tbl = fulltbl.groupby(['price'])[['volume']].sum()
    final_tbl['n_unique_orders'] = fulltbl.groupby('price').address.nunique().astype(float)
    final_tbl['price'] = final_tbl.index
    final_tbl['sqrt'] = np.sqrt(final_tbl['volume'])
    # making the tooltip
    final_tbl['text'] = ("There are " + final_tbl['volume'].map(str) + " ETH available for " + final_tbl['price'].map(
        str) + " BTC being offered by " + final_tbl['n_unique_orders'].map(str) + " ETH addresses")

    # get market price
    mp = public_client.get_product_ticker(product_id='ETH-BTC')
    final_tbl['market price'] = mp['price']

    # makes the type float so that the next logical comparison can take place
    final_tbl['market price'] = final_tbl['market price'].astype(float)

    # determine buys / sells relative to last market price
    final_tbl['color'] = np.where(final_tbl['price'] > final_tbl['market price'], 'red', 'green')

    return final_tbl


# begin building the dash itself
app = dash.Dash()

app.layout = html.Div([
    dcc.Graph(
        id='live-graph',
    ),
    dcc.Graph(
        id='live-graph-ethbtc',
    ),
    dcc.Interval(
        id='interval-component',
        interval=1 * 10000  # in milliseconds for the automatic refresh
    )
])


# links up the chart creation to the interval for an auto-refresh
@app.callback(Output('live-graph', 'figure'),
              events=[Event('interval-component', 'interval')])
def update_graph():
    result = get_data()
    return {
        'data': [
            go.Scatter(
                x=result['volume'],
                y=result['price'],
                mode='markers',
                text= result['text'],
                opacity=0.7,
                hoverinfo='text',
                marker={
                    'size': result['sqrt'],
                    'line': {'width': 0.5, 'color': 'white'},
                    'color': result['color']  # set color equal to variable
                },

            )
        ],
        'layout': go.Layout(
            # makes it so that title automatically updates with refreshed market price as well
            title=("The present market price of ETH is: $" + str(result['market price'].iloc[0])),
            xaxis={'title': 'Order Size'},
            yaxis={'title': 'ETH Price'},
            hovermode='closest'
        )
    }


# BTCETH#
@app.callback(Output('live-graph-ethbtc', 'figure'),
              events=[Event('interval-component', 'interval')])
def update_graph_ethbtc():
    result = get_data_ethbtc()
    return {
        'data': [
            go.Scatter(
                x=result['volume'],
                y=result['price'],
                mode='markers',
                text=result['text'],
                opacity=0.7,
                hoverinfo='text',
                marker={
                    'size': result['sqrt'],
                    'line': {'width': 0.5, 'color': 'white'},
                    'color': result['color']
                },

            )
        ],
        'layout': go.Layout(
            # makes it so that title automatically updates with refreshed market price as well
            title=("The present market price of ETHBTC is: $" + str(result['market price'].iloc[0])),
            xaxis={'title': 'Order Size'},
            yaxis={'title': 'ETHBTC Price'},
            hovermode='closest'
        )
    }


if __name__ == '__main__':
    app.run_server(host='0.0.0.0')
