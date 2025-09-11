# lotterybr

<!-- badges: start -->


<!-- badges: end -->

The goal of the package is to provide a function to automatically import
data from the lotteries of Caixa Economica Federal into the Python
environment. Data from the lotteries of Caixa Economica Federal includes
information on various games such as Mega-Sena, Lotofacil, Quina, among
others. They are downloaded from the official website of the Federal
Savings Bank at <https://loterias.caixa.gov.br/>.

## Installation

You can install the development version of lotterybr like so:

``` python
pip install lotterybr
```

## Example

Downloading Lotofacil winners data:

``` python

from lotterybr import get_data

lotofacil = get_data(game= "lotofacil", type= "winners")
```