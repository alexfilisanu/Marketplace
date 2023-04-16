"""
This module represents the Marketplace.

Computer Systems Architecture Course
Assignment 1
March 2021
"""

from threading import Lock
import logging
from time import gmtime, strftime
from logging.handlers import RotatingFileHandler
import unittest

LOGGER = logging.getLogger()
LOGGER.setLevel(logging.INFO)
LOGGER.addHandler(RotatingFileHandler(filename='marketplace.log', maxBytes=4096, backupCount=10))
TIMESTAMP = strftime('%Y-%m-%d %H:%M:%S', gmtime())

class Marketplace:
    """
    Class that represents the Marketplace. It's the central part of the implementation.
    The producers and consumers use its methods concurrently.
    """
    def __init__(self, queue_size_per_producer):
        """
        Constructor

        :type queue_size_per_producer: Int
        :param queue_size_per_producer: the maximum size of a queue associated with each producer
        """
        self.queue_size_per_producer = queue_size_per_producer
        # dictionar in care vor fi inserate valor de forma: key: Int - id ul producatorului,
        # value: [] - lista de produse ale respectivului producator
        self.producers_dictionary = {}
        # dictionar in care vor fi inserate valor de forma: key: Int - id ul cosului de cumparaturi,
        # value: [] - lista de produse ale respectivului cos - un prdus este de forma (producer_id,
        # product)
        self.carts_dictionary = {}
        # lock folosit pentru atunci cand un producer este inregistrat
        self.register_producer_lock = Lock()
        # lock folosit pentru atunci cand un produs este publish in marketplace
        self.publish_lock = Lock()
        # lock folosit pentru atunci cand un produs este mutat din lista intr un cos de cumparaturi
        self.add_to_cart_lock = Lock()
        # lock folosit pentru atunci cand un nou cart este inregistart
        self.new_cart_lock = Lock()

    def register_producer(self):
        """
        Returns an id for the producer that calls this.
        """
        LOGGER.info('%s: Start register_producer', TIMESTAMP)

        with self.register_producer_lock:
            producer_id = len(self.producers_dictionary)
            self.producers_dictionary[producer_id] = []

        LOGGER.info('%s: Registered producer_id %s', TIMESTAMP, producer_id)
        return producer_id

    def publish(self, producer_id, product):
        """
        Adds the product provided by the producer to the marketplace

        :type producer_id: String
        :param producer_id: producer id

        :type product: Product
        :param product: the Product that will be published in the Marketplace

        :returns True or False. If the caller receives False, it should wait and then try again.
        """
        LOGGER.info('%s: Start publish with product %s and producer_id %s',
                    TIMESTAMP, product, producer_id)
        producer_queue = self.producers_dictionary[producer_id]

        # un singur produs poate fi adaugat in lista produselor la un moment de timp
        with self.publish_lock:
            # daca este loc in lista => adaug produsul + return True, altfel return False
            if len(producer_queue) < self.queue_size_per_producer:
                producer_queue.append(product)
                LOGGER.info('%s: Published product %s from producer_id %s',
                            TIMESTAMP, product, producer_id)
                return True

        LOGGER.info('%s: Producer Queue is full. Cannot publish product %s from producer_id %s',
                    TIMESTAMP, product, producer_id)
        return False

    def new_cart(self):
        """
        Creates a new cart for the consumer

        :returns an int representing the cart_id
        """
        LOGGER.info('%s: Start new_cart', TIMESTAMP)

        with self.new_cart_lock:
            cart_id = len(self.carts_dictionary)
            self.carts_dictionary[cart_id] = []

        LOGGER.info('%s: New cart_id %s', TIMESTAMP, cart_id)
        return cart_id

    def add_to_cart(self, cart_id, product):
        """
        Adds a product to the given cart. The method returns

        :type cart_id: Int
        :param cart_id: id cart

        :type product: Product
        :param product: the product to add to cart

        :returns True or False. If the caller receives False, it should wait and then try again
        """
        LOGGER.info('%s: Start add_to_cart with product %s and cart_id %s',
                    TIMESTAMP, product, cart_id)
        cart = self.carts_dictionary[cart_id]

        # un singur produs poate fi adaugat in cos la un moment de timp
        with self.add_to_cart_lock:
            # iterez prin toate produsele tuturor producatorilor
            for producer_id, producer_queue in self.producers_dictionary.items():
                for i, (prod) in enumerate(producer_queue):
                    # daca am gasit produsul cautat, il adaug in cosul de cumparturi, sub
                    # forma(producer_id, product) + il sterg din lista produselor +
                    # return True; altfel return False
                    if prod == product:
                        cart.append((producer_id, prod))
                        self.producers_dictionary[producer_id].pop(i)
                        LOGGER.info('%s: Added product %s to cart_id %s',
                                    TIMESTAMP, product, cart_id)
                        return True

        LOGGER.info('%s: Cannot add product %s to cart_id %s', TIMESTAMP, product, cart_id)
        return False

    def remove_from_cart(self, cart_id, product):
        """
        Removes a product from cart.

        :type cart_id: Int
        :param cart_id: id cart

        :type product: Product
        :param product: the product to remove from cart
        """
        LOGGER.info('%s: Start remove_from_cart with product %s and cart_id %s',
                    TIMESTAMP, product, cart_id)
        cart = self.carts_dictionary[cart_id]

        # iterez prin toate produsele din cos
        for i, (id_prod, prod) in enumerate(cart):
            # daca am gasit produsul cautat, il sterg din cosul de cumparturi +
            # il adaug inapoi in lista producatorului sau
            if prod == product:
                cart.pop(i)
                self.producers_dictionary[id_prod].append(product)
                LOGGER.info('%s: Removed product %s from cart_id %s', TIMESTAMP, product, cart_id)
                return

        LOGGER.info('%s: Cannot remove product %s from cart_id %s', TIMESTAMP, product, cart_id)

    def place_order(self, cart_id):
        """
        Return a list with all the products in the cart.

        :type cart_id: Int
        :param cart_id: id cart
        """
        LOGGER.info('%s: Start place_order for cart_id %s', TIMESTAMP, cart_id)
        cart = self.carts_dictionary[cart_id]

        # adaug doar produsele(al doilea element din tuple) in lista pe care o returnez
        products_list = list(map(lambda x: x[1], cart))
        LOGGER.info('%s: Placed order cart_id %s', TIMESTAMP, cart_id)

        return products_list

class TestMarketplace(unittest.TestCase):
    """
    A class for testing the functionality of the Marketplace class.
    """
    def setUp(self):
        self.marketplace = Marketplace(queue_size_per_producer=3)
        self.producer_id = 0
        self.marketplace.producers_dictionary[self.producer_id] = []
        self.cart_id = 0
        self.marketplace.carts_dictionary[self.cart_id] = []
        self.product_coffee = {
            "product_type": "Coffee",
            "name": "Indonezia",
            "acidity": 5.05,
            "roast_level": "MEDIUM",
            "price": 1
        }
        self.product_tea = {
            "product_type": "Tea",
            "name": "Linden",
            "type": "Herbal",
            "price": 9
        }

    def test_register_producer(self):
        """
        Tests if a producer is correctly registered in the marketplace.
        """
        test_producer_id = self.marketplace.register_producer()

        self.assertIsInstance(test_producer_id, int)
        self.assertEqual(test_producer_id, 1)

    def test_publish_empty_queue(self):
        """
        Tests if a product is correctly published to an empty producer queue.
        """
        self.assertTrue(self.marketplace.publish(self.producer_id, self.product_coffee))
        self.assertIn(self.product_coffee, self.marketplace.producers_dictionary[self.producer_id])

    def test_publish_full_queue(self):
        """
        Tests if a product behaves correctly when producer queue is full.
        """
        for i in range(self.marketplace.queue_size_per_producer + 1):
            if i < self.marketplace.queue_size_per_producer:
                self.assertTrue(self.marketplace.publish(self.producer_id, self.product_coffee))
            else:
                self.assertFalse(self.marketplace.publish(self.producer_id, self.product_coffee))

    def test_new_cart(self):
        """
        Tests if a producer is correctly created in the marketplace.
        """
        test_cart_id = self.marketplace.new_cart()

        self.assertIsInstance(test_cart_id, int)
        self.assertEqual(test_cart_id, 1)

    def test_add_to_cart_published_product(self):
        """
        Tests if a published product is correctly added to a cart.
        """
        self.marketplace.publish(self.producer_id, self.product_coffee)

        self.assertTrue(self.marketplace.add_to_cart(self.cart_id, self.product_coffee))
        self.assertIn((self.producer_id, self.product_coffee),
                      self.marketplace.carts_dictionary[self.cart_id])
        self.assertEqual(len(self.marketplace.carts_dictionary[self.cart_id]), 1)

    def test_add_to_cart_unpublished_product(self):
        """
        Tests if an unpublished product behaves correctly when trying to add it to a cart.
        """
        self.assertFalse(self.marketplace.add_to_cart(self.cart_id, self.product_coffee))
        self.assertEqual(len(self.marketplace.carts_dictionary[self.cart_id]), 0)

    def test_remove_from_cart(self):
        """
        Tests if a product is correctly removed from a cart.
        """
        self.marketplace.publish(self.producer_id, self.product_coffee)
        self.marketplace.add_to_cart(self.cart_id, self.product_coffee)
        self.marketplace.remove_from_cart(self.cart_id, self.product_coffee)

        self.assertNotIn(self.product_coffee, self.marketplace.carts_dictionary[self.cart_id])
        self.assertEqual(len(self.marketplace.carts_dictionary[self.cart_id]), 0)

    def test_place_order(self):
        """
        Tests if an order is correctly placed.
        """
        self.marketplace.publish(self.producer_id, self.product_coffee)
        self.marketplace.publish(self.producer_id, self.product_tea)
        self.marketplace.add_to_cart(self.cart_id, self.product_coffee)
        self.marketplace.add_to_cart(self.cart_id, self.product_tea)
        order = self.marketplace.place_order(self.cart_id)

        self.assertIsInstance(order, list)
        self.assertEqual(len(order), 2)
        self.assertEqual(order[0], self.product_coffee)
        self.assertEqual(order[1], self.product_tea)
