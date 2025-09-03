import re
from typing import Dict, List, Optional, Tuple, Set
from enum import Enum
import logging
from difflib import SequenceMatcher
from collections import defaultdict

logger = logging.getLogger(__name__)


class ProductCategory(Enum):
    """Product category enumeration."""
    VEGETABLES = "vegetables"
    FRUITS = "fruits"
    MEAT = "meat"
    DAIRY = "dairy"
    BAKERY = "bakery"
    BEVERAGES = "beverages"
    PANTRY = "pantry"
    SNACKS = "snacks"
    FROZEN = "frozen"
    HOUSEHOLD = "household"
    PERSONAL_CARE = "personal-care"
    BABY_CARE = "baby-care"
    HEALTH = "health"
    PET = "pet"
    ELECTRONICS = "electronics"
    CLOTHING = "clothing"
    UNKNOWN = "unknown"


class CategoryClassifier:
    """Advanced product category classifier using multiple classification methods."""
    
    def __init__(self):
        self.category_keywords = self._build_category_keywords()
        self.brand_categories = self._build_brand_categories()
        self.unit_patterns = self._build_unit_patterns()
        self.exclusion_patterns = self._build_exclusion_patterns()
        
    def _build_category_keywords(self) -> Dict[ProductCategory, Dict[str, float]]:
        """Build comprehensive keyword mappings with weights."""
        return {
            ProductCategory.VEGETABLES: {
                # Primary vegetables
                'tomato': 1.0, 'tomatoes': 1.0, 'potato': 1.0, 'potatoes': 1.0,
                'onion': 1.0, 'onions': 1.0, 'carrot': 1.0, 'carrots': 1.0,
                'cucumber': 1.0, 'lettuce': 1.0, 'spinach': 1.0, 'cabbage': 1.0,
                'pepper': 0.8, 'peppers': 0.8, 'bell': 0.7, 'capsicum': 1.0,
                'broccoli': 1.0, 'cauliflower': 1.0, 'zucchini': 1.0, 'eggplant': 1.0,
                'garlic': 1.0, 'ginger': 1.0, 'celery': 1.0, 'radish': 1.0,
                'beetroot': 1.0, 'turnip': 1.0, 'leek': 1.0, 'corn': 0.8,
                'peas': 0.8, 'beans': 0.7, 'okra': 1.0, 'artichoke': 1.0,
                'asparagus': 1.0, 'mushroom': 0.9, 'mushrooms': 0.9,
                # Arabic names
                '7E'7E': 1.0, '(7'73': 1.0, '(5D': 1.0, ',21': 1.0,
                '.J'1': 1.0, '.3': 1.0, '3('F.': 1.0, 'EDAHA': 1.0,
                # Context words
                'fresh': 0.6, 'organic': 0.6, 'local': 0.5, 'seasonal': 0.5,
                'vegetable': 0.9, 'vegetables': 0.9, 'veggie': 0.8, 'produce': 0.7,
            },
            
            ProductCategory.FRUITS: {
                # Common fruits
                'apple': 1.0, 'apples': 1.0, 'banana': 1.0, 'bananas': 1.0,
                'orange': 1.0, 'oranges': 1.0, 'grape': 1.0, 'grapes': 1.0,
                'strawberry': 1.0, 'strawberries': 1.0, 'mango': 1.0, 'mangoes': 1.0,
                'pineapple': 1.0, 'watermelon': 1.0, 'melon': 1.0, 'cantaloupe': 1.0,
                'peach': 1.0, 'peaches': 1.0, 'pear': 1.0, 'pears': 1.0,
                'cherry': 1.0, 'cherries': 1.0, 'plum': 1.0, 'plums': 1.0,
                'kiwi': 1.0, 'avocado': 1.0, 'lemon': 1.0, 'lemons': 1.0,
                'lime': 1.0, 'limes': 1.0, 'grapefruit': 1.0, 'pomegranate': 1.0,
                'blueberry': 1.0, 'blueberries': 1.0, 'raspberry': 1.0, 'blackberry': 1.0,
                'coconut': 1.0, 'dates': 1.0, 'figs': 1.0, 'apricot': 1.0,
                # Arabic names
                '*A'-': 1.0, 'EH2': 1.0, '(1*B'D': 1.0, '9F(': 1.0,
                'A1'HD)': 1.0, 'E'F,H': 1.0, '#F'F'3': 1.0, '(7J.': 1.0,
                # Context words
                'fruit': 0.9, 'fruits': 0.9, 'citrus': 0.8, 'berry': 0.8, 'berries': 0.8,
                'tropical': 0.7, 'seasonal': 0.5, 'fresh': 0.6, 'ripe': 0.6,
            },
            
            ProductCategory.MEAT: {
                # Meat types
                'chicken': 1.0, 'beef': 1.0, 'lamb': 1.0, 'mutton': 1.0,
                'pork': 1.0, 'turkey': 1.0, 'duck': 1.0, 'veal': 1.0,
                'goat': 1.0, 'rabbit': 0.9, 'venison': 1.0,
                # Cuts and preparations
                'breast': 0.7, 'thigh': 0.7, 'wing': 0.7, 'drumstick': 0.8,
                'steak': 0.9, 'chops': 0.9, 'roast': 0.8, 'mince': 0.9,
                'ground': 0.8, 'fillet': 0.8, 'cutlet': 0.8, 'ribs': 0.9,
                'sausage': 0.9, 'bacon': 1.0, 'ham': 1.0, 'salami': 1.0,
                'pepperoni': 1.0, 'bratwurst': 1.0, 'chorizo': 1.0,
                # Seafood
                'fish': 0.9, 'salmon': 1.0, 'tuna': 1.0, 'cod': 1.0,
                'shrimp': 1.0, 'prawns': 1.0, 'lobster': 1.0, 'crab': 1.0,
                'oyster': 1.0, 'mussels': 1.0, 'scallops': 1.0, 'calamari': 1.0,
                'sardines': 1.0, 'mackerel': 1.0, 'sea bass': 1.0, 'tilapia': 1.0,
                # Arabic names
                '/,',': 1.0, 'D-E': 1.0, '.1HA': 1.0, '(B1': 1.0,
                '3EC': 1.0, ',E(1J': 1.0, 'C'(H1J'': 1.0,
                # Context words
                'meat': 0.9, 'poultry': 0.9, 'seafood': 0.9, 'protein': 0.7,
                'fresh': 0.6, 'frozen': 0.6, 'organic': 0.5, 'halal': 0.6,
                'butcher': 0.8, 'deli': 0.7,
            },
            
            ProductCategory.DAIRY: {
                # Dairy products
                'milk': 1.0, 'cheese': 1.0, 'butter': 1.0, 'cream': 0.8,
                'yogurt': 1.0, 'yoghurt': 1.0, 'kefir': 1.0, 'sour cream': 1.0,
                'cottage cheese': 1.0, 'mozzarella': 1.0, 'cheddar': 1.0, 'feta': 1.0,
                'parmesan': 1.0, 'gouda': 1.0, 'brie': 1.0, 'camembert': 1.0,
                'ricotta': 1.0, 'mascarpone': 1.0, 'cream cheese': 1.0,
                'whipped cream': 1.0, 'heavy cream': 1.0, 'half and half': 1.0,
                # Eggs
                'eggs': 1.0, 'egg': 1.0, 'dozen': 0.7, 'quail': 0.8,
                # Alternatives
                'almond milk': 0.9, 'soy milk': 0.9, 'oat milk': 0.9,
                'coconut milk': 0.8, 'rice milk': 0.9, 'cashew milk': 0.9,
                # Arabic names
                'D(F': 1.0, ',(F': 1.0, '2(/)': 1.0, '2('/J': 1.0,
                '(J6': 1.0, 'C1JE)': 0.8,
                # Context words
                'dairy': 1.0, 'lactose': 0.7, 'calcium': 0.6, 'pasteurized': 0.6,
                'full fat': 0.6, 'low fat': 0.6, 'skim': 0.7, 'whole': 0.5,
            },
            
            ProductCategory.BAKERY: {
                # Bread
                'bread': 1.0, 'loaf': 0.9, 'baguette': 1.0, 'roll': 0.8, 'rolls': 0.8,
                'pita': 1.0, 'naan': 1.0, 'tortilla': 1.0, 'bagel': 1.0, 'croissant': 1.0,
                'muffin': 1.0, 'scone': 1.0, 'biscuit': 0.8, 'toast': 0.8,
                'sandwich': 0.7, 'burger bun': 0.9, 'hot dog bun': 0.9,
                # Pastries
                'cake': 1.0, 'cupcake': 1.0, 'pie': 0.8, 'tart': 0.9, 'pastry': 1.0,
                'donut': 1.0, 'danish': 1.0, 'strudel': 1.0, 'eclair': 1.0,
                'profiterole': 1.0, 'macaron': 1.0, 'cookie': 0.8, 'brownie': 1.0,
                # Arabic names
                '.(2': 1.0, '9J4': 1.0, 'CJC': 1.0, 'C9C': 1.0,
                '(3CHJ*': 0.8, 'C1H'3HF': 1.0,
                # Context words
                'bakery': 1.0, 'baked': 0.8, 'fresh': 0.6, 'artisan': 0.7,
                'whole grain': 0.7, 'multigrain': 0.7, 'sourdough': 0.8,
                'gluten free': 0.7, 'organic': 0.5,
            },
            
            ProductCategory.BEVERAGES: {
                # Non-alcoholic
                'water': 0.9, 'juice': 1.0, 'soda': 1.0, 'cola': 1.0, 'pepsi': 1.0,
                'sprite': 1.0, 'fanta': 1.0, 'tea': 1.0, 'coffee': 1.0,
                'cappuccino': 1.0, 'latte': 1.0, 'espresso': 1.0, 'americano': 1.0,
                'energy drink': 1.0, 'sports drink': 1.0, 'smoothie': 1.0,
                'milkshake': 1.0, 'lemonade': 1.0, 'iced tea': 1.0,
                'kombucha': 1.0, 'coconut water': 1.0, 'sparkling water': 1.0,
                # Alcoholic
                'beer': 1.0, 'wine': 1.0, 'whiskey': 1.0, 'vodka': 1.0,
                'rum': 1.0, 'gin': 1.0, 'tequila': 1.0, 'brandy': 1.0,
                'champagne': 1.0, 'cocktail': 1.0, 'liqueur': 1.0,
                # Arabic names
                '95J1': 1.0, 'EJ'G': 0.9, '4'J': 1.0, 'BGH)': 1.0,
                'CHD'': 1.0, 'E41H(': 0.8,
                # Context words
                'drink': 0.8, 'beverage': 1.0, 'refreshing': 0.6, 'cold': 0.5,
                'hot': 0.5, 'iced': 0.6, 'fizzy': 0.7, 'carbonated': 0.7,
                'bottle': 0.5, 'can': 0.5, 'pack': 0.4, 'liter': 0.5, 'ml': 0.4,
            },
            
            ProductCategory.PANTRY: {
                # Grains and cereals
                'rice': 1.0, 'pasta': 1.0, 'noodles': 1.0, 'cereal': 1.0,
                'oats': 1.0, 'quinoa': 1.0, 'barley': 1.0, 'wheat': 1.0,
                'flour': 1.0, 'breadcrumbs': 1.0, 'couscous': 1.0,
                # Canned goods
                'canned': 0.8, 'can': 0.6, 'tomato sauce': 1.0, 'paste': 0.8,
                'beans': 0.8, 'lentils': 1.0, 'chickpeas': 1.0, 'corn': 0.7,
                'soup': 0.9, 'broth': 1.0, 'stock': 1.0, 'sauce': 0.7,
                # Condiments and spices
                'salt': 1.0, 'pepper': 0.7, 'sugar': 1.0, 'honey': 1.0,
                'oil': 0.9, 'olive oil': 1.0, 'vinegar': 1.0, 'mustard': 1.0,
                'ketchup': 1.0, 'mayonnaise': 1.0, 'soy sauce': 1.0,
                'hot sauce': 1.0, 'bbq sauce': 1.0, 'salad dressing': 1.0,
                'herbs': 0.8, 'spices': 0.9, 'seasoning': 0.9, 'marinade': 1.0,
                # Baking
                'baking powder': 1.0, 'baking soda': 1.0, 'vanilla': 1.0,
                'yeast': 1.0, 'cocoa': 1.0, 'chocolate chips': 0.9,
                # Arabic names
                '#12': 1.0, 'EC1HF)': 1.0, '/BJB': 1.0, '3C1': 1.0,
                'ED-': 1.0, '2J*': 0.9, '93D': 1.0, '5D5)': 0.7,
                # Context words
                'pantry': 1.0, 'staple': 0.8, 'ingredient': 0.7, 'cooking': 0.6,
                'dry goods': 0.8, 'shelf stable': 0.7, 'preserves': 0.8,
            },
            
            ProductCategory.SNACKS: {
                # Chips and crackers
                'chips': 1.0, 'crisps': 1.0, 'crackers': 1.0, 'pretzels': 1.0,
                'popcorn': 1.0, 'tortilla chips': 1.0, 'corn chips': 1.0,
                'rice cakes': 1.0, 'wafers': 1.0, 'biscuits': 0.8,
                # Nuts and seeds
                'nuts': 1.0, 'almonds': 1.0, 'walnuts': 1.0, 'cashews': 1.0,
                'peanuts': 1.0, 'pistachios': 1.0, 'hazelnuts': 1.0,
                'sunflower seeds': 1.0, 'pumpkin seeds': 1.0, 'trail mix': 1.0,
                # Sweet snacks
                'chocolate': 1.0, 'candy': 1.0, 'gummy': 1.0, 'lollipop': 1.0,
                'marshmallow': 1.0, 'cookie': 0.8, 'granola bar': 1.0,
                'protein bar': 1.0, 'energy bar': 1.0, 'fruit snacks': 1.0,
                # Arabic names
                '4J(3': 1.0, '(3CHJ*': 0.8, '4HCHD'*)': 1.0, '-DHI': 1.0,
                'DH2': 1.0, 'AHD 3H/'FJ': 1.0, 'A3*B': 1.0,
                # Context words
                'snack': 1.0, 'snacks': 1.0, 'crunchy': 0.7, 'crispy': 0.7,
                'sweet': 0.6, 'salty': 0.6, 'healthy': 0.5, 'organic': 0.5,
                'pack': 0.5, 'bag': 0.5, 'portion': 0.5,
            },
            
            ProductCategory.FROZEN: {
                # Frozen foods
                'frozen': 1.0, 'ice cream': 1.0, 'sorbet': 1.0, 'gelato': 1.0,
                'popsicle': 1.0, 'frozen yogurt': 1.0, 'sherbet': 1.0,
                'frozen meal': 1.0, 'tv dinner': 1.0, 'frozen pizza': 1.0,
                'frozen vegetables': 1.0, 'frozen fruits': 1.0, 'frozen berries': 1.0,
                'ice': 0.8, 'freezer': 0.7, 'thaw': 0.7, 'defrost': 0.7,
                # Arabic names
                'E+D,'*': 1.0, '"J3 C1JE': 1.0, 'E,E/': 1.0,
                # Context words
                'keep frozen': 0.8, 'freezer section': 0.8, 'frost': 0.6,
                'temperature': 0.5, 'cold': 0.5,
            },
            
            ProductCategory.HOUSEHOLD: {
                # Cleaning supplies
                'detergent': 1.0, 'soap': 0.8, 'cleaner': 1.0, 'disinfectant': 1.0,
                'bleach': 1.0, 'fabric softener': 1.0, 'stain remover': 1.0,
                'dishwashing': 1.0, 'laundry': 1.0, 'floor cleaner': 1.0,
                'glass cleaner': 1.0, 'bathroom cleaner': 1.0, 'kitchen cleaner': 1.0,
                'toilet paper': 1.0, 'paper towels': 1.0, 'tissues': 1.0,
                'napkins': 1.0, 'plates': 0.8, 'cups': 0.7, 'utensils': 0.8,
                'aluminum foil': 1.0, 'plastic wrap': 1.0, 'garbage bags': 1.0,
                'storage bags': 1.0, 'containers': 0.7, 'batteries': 1.0,
                'light bulbs': 1.0, 'candles': 1.0, 'matches': 1.0,
                # Arabic names
                'EF8A': 1.0, '5'(HF': 0.8, 'E7G1': 1.0, 'EF'/JD': 1.0,
                'H1B *H'DJ*': 1.0, '#CJ'3': 0.8, '(7'1J'*': 1.0,
                # Context words
                'cleaning': 1.0, 'household': 1.0, 'home': 0.6, 'kitchen': 0.6,
                'bathroom': 0.7, 'laundry room': 0.8, 'supplies': 0.8,
            },
            
            ProductCategory.PERSONAL_CARE: {
                # Personal hygiene
                'shampoo': 1.0, 'conditioner': 1.0, 'body wash': 1.0, 'soap': 0.7,
                'toothpaste': 1.0, 'toothbrush': 1.0, 'mouthwash': 1.0,
                'deodorant': 1.0, 'antiperspirant': 1.0, 'perfume': 1.0,
                'cologne': 1.0, 'lotion': 1.0, 'moisturizer': 1.0,
                'sunscreen': 1.0, 'face wash': 1.0, 'cleanser': 1.0,
                'toner': 1.0, 'serum': 1.0, 'cream': 0.7, 'mask': 0.8,
                'razor': 1.0, 'shaving cream': 1.0, 'aftershave': 1.0,
                'nail polish': 1.0, 'makeup': 1.0, 'lipstick': 1.0,
                'foundation': 0.9, 'mascara': 1.0, 'eyeshadow': 1.0,
                # Arabic names
                '4'E(H': 1.0, '5'(HF': 0.7, 'E9,HF #3F'F': 1.0, '971': 1.0,
                'C1JE': 0.7, 'E2JD 91B': 1.0, ':3HD': 1.0,
                # Context words
                'personal care': 1.0, 'hygiene': 1.0, 'beauty': 0.9,
                'skincare': 1.0, 'hair care': 1.0, 'oral care': 1.0,
                'cosmetics': 1.0, 'grooming': 1.0,
            },
            
            ProductCategory.BABY_CARE: {
                # Baby products
                'baby': 1.0, 'infant': 1.0, 'newborn': 1.0, 'toddler': 0.8,
                'diapers': 1.0, 'nappies': 1.0, 'wipes': 1.0, 'baby wipes': 1.0,
                'baby food': 1.0, 'formula': 1.0, 'baby milk': 1.0,
                'baby bottle': 1.0, 'pacifier': 1.0, 'teething': 1.0,
                'baby shampoo': 1.0, 'baby soap': 1.0, 'baby lotion': 1.0,
                'baby powder': 1.0, 'rash cream': 1.0, 'baby oil': 1.0,
                'stroller': 1.0, 'car seat': 1.0, 'high chair': 1.0,
                'baby carrier': 1.0, 'crib': 1.0, 'bassinet': 1.0,
                # Arabic names
                '7AD': 1.0, '16J9': 1.0, '-A'6'*': 1.0, 'EF'/JD #7A'D': 1.0,
                '79'E #7A'D': 1.0, 'D(F #7A'D': 1.0, '4'E(H #7A'D': 1.0,
                # Context words
                'pediatric': 1.0, 'child': 0.7, 'kids': 0.6, 'nursery': 0.8,
                'months': 0.6, 'years': 0.5, 'gentle': 0.6, 'hypoallergenic': 0.7,
            },
            
            ProductCategory.HEALTH: {
                # Medications and supplements
                'medicine': 1.0, 'medication': 1.0, 'pills': 1.0, 'tablets': 1.0,
                'capsules': 1.0, 'syrup': 0.9, 'drops': 0.8, 'ointment': 1.0,
                'cream': 0.7, 'gel': 0.8, 'spray': 0.7, 'patch': 0.8,
                'vitamin': 1.0, 'supplement': 1.0, 'protein': 0.8,
                'calcium': 1.0, 'iron': 0.9, 'zinc': 1.0, 'magnesium': 1.0,
                'omega': 1.0, 'probiotics': 1.0, 'multivitamin': 1.0,
                'pain relief': 1.0, 'aspirin': 1.0, 'ibuprofen': 1.0,
                'acetaminophen': 1.0, 'antibiotic': 1.0, 'antacid': 1.0,
                'cough': 1.0, 'cold': 0.7, 'allergy': 1.0, 'fever': 0.8,
                'thermometer': 1.0, 'bandage': 1.0, 'first aid': 1.0,
                # Arabic names
                '/H'!': 1.0, '-(H(': 1.0, 'AJ*'EJF': 1.0, 'ECED :0'&J': 1.0,
                'E3CF': 1.0, 'E6'/ -JHJ': 1.0, 'C1JE': 0.7, 'E1GE': 1.0,
                # Context words
                'pharmacy': 1.0, 'medical': 1.0, 'health': 1.0, 'wellness': 1.0,
                'prescription': 0.8, 'over-the-counter': 1.0, 'otc': 1.0,
                'therapeutic': 0.9, 'clinical': 0.8,
            },
        }
    
    def _build_brand_categories(self) -> Dict[str, ProductCategory]:
        """Build brand-to-category mappings."""
        return {
            # Dairy brands
            'almarai': ProductCategory.DAIRY,
            'juhayna': ProductCategory.DAIRY,
            'domty': ProductCategory.DAIRY,
            'beyti': ProductCategory.DAIRY,
            'nada': ProductCategory.DAIRY,
            'dannon': ProductCategory.DAIRY,
            'chobani': ProductCategory.DAIRY,
            'yoplait': ProductCategory.DAIRY,
            'philadelphia': ProductCategory.DAIRY,
            
            # Beverage brands
            'coca-cola': ProductCategory.BEVERAGES,
            'pepsi': ProductCategory.BEVERAGES,
            'sprite': ProductCategory.BEVERAGES,
            'fanta': ProductCategory.BEVERAGES,
            'nestle': ProductCategory.BEVERAGES,
            'tropicana': ProductCategory.BEVERAGES,
            'fresh': ProductCategory.BEVERAGES,
            'baraka': ProductCategory.BEVERAGES,
            'hayat': ProductCategory.BEVERAGES,
            'aquafina': ProductCategory.BEVERAGES,
            
            # Snack brands
            'lays': ProductCategory.SNACKS,
            'pringles': ProductCategory.SNACKS,
            'doritos': ProductCategory.SNACKS,
            'cheetos': ProductCategory.SNACKS,
            'oreo': ProductCategory.SNACKS,
            'kitkat': ProductCategory.SNACKS,
            'snickers': ProductCategory.SNACKS,
            'twix': ProductCategory.SNACKS,
            'mars': ProductCategory.SNACKS,
            'cadbury': ProductCategory.SNACKS,
            
            # Household brands
            'ariel': ProductCategory.HOUSEHOLD,
            'tide': ProductCategory.HOUSEHOLD,
            'persil': ProductCategory.HOUSEHOLD,
            'fairy': ProductCategory.HOUSEHOLD,
            'mr clean': ProductCategory.HOUSEHOLD,
            'lysol': ProductCategory.HOUSEHOLD,
            'clorox': ProductCategory.HOUSEHOLD,
            'downy': ProductCategory.HOUSEHOLD,
            'bounce': ProductCategory.HOUSEHOLD,
            
            # Personal care brands
            'johnson': ProductCategory.PERSONAL_CARE,
            'nivea': ProductCategory.PERSONAL_CARE,
            'dove': ProductCategory.PERSONAL_CARE,
            'olay': ProductCategory.PERSONAL_CARE,
            'pantene': ProductCategory.PERSONAL_CARE,
            'head shoulders': ProductCategory.PERSONAL_CARE,
            'loreal': ProductCategory.PERSONAL_CARE,
            'garnier': ProductCategory.PERSONAL_CARE,
            'colgate': ProductCategory.PERSONAL_CARE,
            'oral-b': ProductCategory.PERSONAL_CARE,
            
            # Baby care brands
            'pampers': ProductCategory.BABY_CARE,
            'huggies': ProductCategory.BABY_CARE,
            'johnson baby': ProductCategory.BABY_CARE,
            'mustela': ProductCategory.BABY_CARE,
            'sebamed': ProductCategory.BABY_CARE,
            'baby dove': ProductCategory.BABY_CARE,
            'chicco': ProductCategory.BABY_CARE,
            'avent': ProductCategory.BABY_CARE,
            
            # Health brands
            'panadol': ProductCategory.HEALTH,
            'advil': ProductCategory.HEALTH,
            'centrum': ProductCategory.HEALTH,
            'pfizer': ProductCategory.HEALTH,
            'gsk': ProductCategory.HEALTH,
            'bayer': ProductCategory.HEALTH,
            'tylenol': ProductCategory.HEALTH,
            'aspirin': ProductCategory.HEALTH,
            'voltaren': ProductCategory.HEALTH,
        }
    
    def _build_unit_patterns(self) -> Dict[ProductCategory, List[str]]:
        """Build unit patterns that suggest categories."""
        return {
            ProductCategory.MEAT: [
                r'\d+\s*kg', r'\d+\s*g\b', r'\d+\s*lb', r'\d+\s*oz',
                r'per\s+kg', r'per\s+lb', r'frozen', r'fresh'
            ],
            ProductCategory.VEGETABLES: [
                r'\d+\s*kg', r'\d+\s*g\b', r'bunch', r'head', r'piece',
                r'organic', r'fresh', r'local'
            ],
            ProductCategory.DAIRY: [
                r'\d+\s*ml', r'\d+\s*l\b', r'\d+\s*oz', r'low\s+fat',
                r'full\s+fat', r'skim', r'whole', r'dozen'
            ],
            ProductCategory.BEVERAGES: [
                r'\d+\s*ml', r'\d+\s*l\b', r'\d+\s*oz', r'bottle', r'can',
                r'pack', r'case', r'carbonated', r'still'
            ],
            ProductCategory.PANTRY: [
                r'\d+\s*g\b', r'\d+\s*kg', r'\d+\s*oz', r'\d+\s*lb',
                r'jar', r'bottle', r'can', r'pack', r'bag'
            ],
        }
    
    def _build_exclusion_patterns(self) -> Dict[ProductCategory, List[str]]:
        """Build patterns that exclude categories."""
        return {
            ProductCategory.MEAT: [
                r'soap', r'shampoo', r'detergent', r'cleaner'
            ],
            ProductCategory.BEVERAGES: [
                r'soap', r'shampoo', r'lotion', r'cream'
            ],
            ProductCategory.PERSONAL_CARE: [
                r'food', r'drink', r'eat', r'meal'
            ],
        }
    
    def classify_product(self, name: str, description: str = None, 
                        brand: str = None, store_category: str = None) -> Tuple[ProductCategory, float]:
        """
        Classify a product using multiple classification methods.
        
        Args:
            name: Product name
            description: Product description (optional)
            brand: Product brand (optional)
            store_category: Store's category classification (optional)
            
        Returns:
            Tuple of (category, confidence_score)
        """
        if not name:
            return ProductCategory.UNKNOWN, 0.0
        
        # Combine all text for analysis
        text_parts = [name.lower()]
        if description:
            text_parts.append(description.lower())
        if brand:
            text_parts.append(brand.lower())
        if store_category:
            text_parts.append(store_category.lower())
        
        combined_text = ' '.join(text_parts)
        
        # Method 1: Direct brand matching (highest confidence)
        if brand:
            brand_category = self._classify_by_brand(brand.lower())
            if brand_category[1] > 0.8:
                return brand_category
        
        # Method 2: Store category mapping
        if store_category:
            store_cat_result = self._classify_by_store_category(store_category.lower())
            if store_cat_result[1] > 0.7:
                return store_cat_result
        
        # Method 3: Keyword-based classification
        keyword_result = self._classify_by_keywords(combined_text)
        
        # Method 4: Pattern-based classification
        pattern_result = self._classify_by_patterns(combined_text)
        
        # Method 5: Context-based classification
        context_result = self._classify_by_context(name.lower(), combined_text)
        
        # Combine results with weighted scoring
        candidates = defaultdict(float)
        
        # Add keyword result (primary method)
        if keyword_result[1] > 0.3:
            candidates[keyword_result[0]] += keyword_result[1] * 0.4
        
        # Add pattern result
        if pattern_result[1] > 0.3:
            candidates[pattern_result[0]] += pattern_result[1] * 0.3
        
        # Add context result
        if context_result[1] > 0.3:
            candidates[context_result[0]] += context_result[1] * 0.2
        
        # Add brand result (if available but not high confidence)
        if brand:
            brand_result = self._classify_by_brand(brand.lower())
            if brand_result[1] > 0.3:
                candidates[brand_result[0]] += brand_result[1] * 0.1
        
        if not candidates:
            return ProductCategory.UNKNOWN, 0.0
        
        # Get the best candidate
        best_category = max(candidates.items(), key=lambda x: x[1])
        
        # Apply exclusion filters
        if self._is_excluded(combined_text, best_category[0]):
            # Try second best if available
            sorted_candidates = sorted(candidates.items(), key=lambda x: x[1], reverse=True)
            if len(sorted_candidates) > 1:
                return sorted_candidates[1][0], sorted_candidates[1][1]
            else:
                return ProductCategory.UNKNOWN, 0.0
        
        return best_category[0], min(best_category[1], 1.0)
    
    def _classify_by_brand(self, brand: str) -> Tuple[ProductCategory, float]:
        """Classify based on brand recognition."""
        brand = brand.strip().lower()
        
        # Direct brand mapping
        if brand in self.brand_categories:
            return self.brand_categories[brand], 0.9
        
        # Partial brand matching
        for known_brand, category in self.brand_categories.items():
            if known_brand in brand or brand in known_brand:
                similarity = SequenceMatcher(None, brand, known_brand).ratio()
                if similarity > 0.8:
                    return category, 0.8 * similarity
        
        return ProductCategory.UNKNOWN, 0.0
    
    def _classify_by_store_category(self, store_category: str) -> Tuple[ProductCategory, float]:
        """Classify based on store's category classification."""
        category_mappings = {
            'dairy': ProductCategory.DAIRY,
            'meat': ProductCategory.MEAT,
            'poultry': ProductCategory.MEAT,
            'seafood': ProductCategory.MEAT,
            'produce': ProductCategory.VEGETABLES,
            'vegetables': ProductCategory.VEGETABLES,
            'fruits': ProductCategory.FRUITS,
            'bakery': ProductCategory.BAKERY,
            'bread': ProductCategory.BAKERY,
            'beverages': ProductCategory.BEVERAGES,
            'drinks': ProductCategory.BEVERAGES,
            'pantry': ProductCategory.PANTRY,
            'grocery': ProductCategory.PANTRY,
            'snacks': ProductCategory.SNACKS,
            'frozen': ProductCategory.FROZEN,
            'household': ProductCategory.HOUSEHOLD,
            'cleaning': ProductCategory.HOUSEHOLD,
            'personal care': ProductCategory.PERSONAL_CARE,
            'beauty': ProductCategory.PERSONAL_CARE,
            'baby': ProductCategory.BABY_CARE,
            'health': ProductCategory.HEALTH,
            'pharmacy': ProductCategory.HEALTH,
            'pet': ProductCategory.PET,
        }
        
        store_category = store_category.strip().lower()
        
        # Direct mapping
        if store_category in category_mappings:
            return category_mappings[store_category], 0.8
        
        # Partial matching
        for category_name, product_category in category_mappings.items():
            if category_name in store_category or store_category in category_name:
                return product_category, 0.7
        
        return ProductCategory.UNKNOWN, 0.0
    
    def _classify_by_keywords(self, text: str) -> Tuple[ProductCategory, float]:
        """Classify based on keyword matching."""
        words = set(re.findall(r'\b\w+\b', text.lower()))
        
        category_scores = defaultdict(float)
        
        for category, keywords in self.category_keywords.items():
            for keyword, weight in keywords.items():
                if keyword in text.lower():
                    # Exact phrase matching
                    category_scores[category] += weight
                elif any(word == keyword for word in words):
                    # Individual word matching
                    category_scores[category] += weight * 0.8
                elif any(keyword in word or word in keyword for word in words):
                    # Partial word matching
                    similarity = max(SequenceMatcher(None, keyword, word).ratio() 
                                   for word in words if len(word) > 2)
                    if similarity > 0.7:
                        category_scores[category] += weight * similarity * 0.6
        
        if not category_scores:
            return ProductCategory.UNKNOWN, 0.0
        
        # Normalize scores
        max_score = max(category_scores.values())
        if max_score > 0:
            for category in category_scores:
                category_scores[category] /= max_score
        
        best_category = max(category_scores.items(), key=lambda x: x[1])
        return best_category[0], best_category[1]
    
    def _classify_by_patterns(self, text: str) -> Tuple[ProductCategory, float]:
        """Classify based on regex patterns."""
        category_scores = defaultdict(float)
        
        for category, patterns in self.unit_patterns.items():
            for pattern in patterns:
                matches = re.findall(pattern, text, re.IGNORECASE)
                if matches:
                    category_scores[category] += len(matches) * 0.5
        
        if not category_scores:
            return ProductCategory.UNKNOWN, 0.0
        
        # Normalize scores
        max_score = max(category_scores.values())
        for category in category_scores:
            category_scores[category] = min(category_scores[category] / max_score, 1.0)
        
        best_category = max(category_scores.items(), key=lambda x: x[1])
        return best_category[0], best_category[1]
    
    def _classify_by_context(self, name: str, text: str) -> Tuple[ProductCategory, float]:
        """Classify based on contextual clues."""
        context_scores = defaultdict(float)
        
        # Check for measurement units
        if re.search(r'\d+\s*(ml|l|liter)', text):
            context_scores[ProductCategory.BEVERAGES] += 0.3
            context_scores[ProductCategory.DAIRY] += 0.2
        
        if re.search(r'\d+\s*(kg|g|gram|lb|pound)', text):
            context_scores[ProductCategory.MEAT] += 0.3
            context_scores[ProductCategory.VEGETABLES] += 0.2
            context_scores[ProductCategory.PANTRY] += 0.2
        
        if re.search(r'\d+\s*(oz|ounce)', text):
            context_scores[ProductCategory.BEVERAGES] += 0.2
            context_scores[ProductCategory.PERSONAL_CARE] += 0.2
        
        # Check for packaging terms
        if re.search(r'\b(bottle|jar|can|pack|bag)\b', text):
            context_scores[ProductCategory.PANTRY] += 0.2
            context_scores[ProductCategory.BEVERAGES] += 0.1
        
        # Check for freshness indicators
        if re.search(r'\b(fresh|organic|natural|farm)\b', text):
            context_scores[ProductCategory.VEGETABLES] += 0.3
            context_scores[ProductCategory.FRUITS] += 0.3
            context_scores[ProductCategory.MEAT] += 0.2
        
        # Check for preparation methods
        if re.search(r'\b(frozen|canned|dried|baked)\b', text):
            context_scores[ProductCategory.FROZEN] += 0.4
            context_scores[ProductCategory.PANTRY] += 0.2
        
        if not context_scores:
            return ProductCategory.UNKNOWN, 0.0
        
        best_category = max(context_scores.items(), key=lambda x: x[1])
        return best_category[0], best_category[1]
    
    def _is_excluded(self, text: str, category: ProductCategory) -> bool:
        """Check if text matches exclusion patterns for a category."""
        if category not in self.exclusion_patterns:
            return False
        
        for pattern in self.exclusion_patterns[category]:
            if re.search(pattern, text, re.IGNORECASE):
                return True
        
        return False
    
    def get_category_confidence_breakdown(self, name: str, description: str = None, 
                                        brand: str = None, store_category: str = None) -> Dict[ProductCategory, float]:
        """
        Get confidence scores for all categories.
        
        Returns:
            Dictionary mapping categories to confidence scores
        """
        if not name:
            return {ProductCategory.UNKNOWN: 1.0}
        
        # Combine all text for analysis
        text_parts = [name.lower()]
        if description:
            text_parts.append(description.lower())
        if brand:
            text_parts.append(brand.lower())
        if store_category:
            text_parts.append(store_category.lower())
        
        combined_text = ' '.join(text_parts)
        
        # Get scores from different methods
        scores = defaultdict(float)
        
        # Keyword-based scores
        keyword_result = self._classify_by_keywords(combined_text)
        if keyword_result[1] > 0:
            scores[keyword_result[0]] += keyword_result[1] * 0.4
        
        # Pattern-based scores
        pattern_result = self._classify_by_patterns(combined_text)
        if pattern_result[1] > 0:
            scores[pattern_result[0]] += pattern_result[1] * 0.3
        
        # Context-based scores
        context_result = self._classify_by_context(name.lower(), combined_text)
        if context_result[1] > 0:
            scores[context_result[0]] += context_result[1] * 0.2
        
        # Brand-based scores
        if brand:
            brand_result = self._classify_by_brand(brand.lower())
            if brand_result[1] > 0:
                scores[brand_result[0]] += brand_result[1] * 0.1
        
        # Normalize scores
        if scores:
            total_score = sum(scores.values())
            if total_score > 0:
                for category in scores:
                    scores[category] = min(scores[category] / total_score, 1.0)
        else:
            scores[ProductCategory.UNKNOWN] = 1.0
        
        return dict(scores)
    
    def suggest_alternative_categories(self, name: str, top_n: int = 3) -> List[Tuple[ProductCategory, float]]:
        """
        Suggest alternative categories for a product.
        
        Returns:
            List of (category, confidence) tuples sorted by confidence
        """
        confidence_breakdown = self.get_category_confidence_breakdown(name)
        
        # Sort by confidence and return top N
        sorted_categories = sorted(confidence_breakdown.items(), 
                                 key=lambda x: x[1], reverse=True)
        
        return sorted_categories[:top_n]


# Global classifier instance
_classifier = CategoryClassifier()


def classify_product(name: str, description: str = None, brand: str = None, 
                    store_category: str = None) -> Tuple[ProductCategory, float]:
    """
    Classify a product into a category.
    
    Args:
        name: Product name
        description: Product description (optional)
        brand: Product brand (optional)
        store_category: Store's category classification (optional)
        
    Returns:
        Tuple of (category, confidence_score)
    """
    return _classifier.classify_product(name, description, brand, store_category)


def get_category_name(category: ProductCategory) -> str:
    """Get human-readable category name."""
    return category.value.replace('-', ' ').title()


def get_all_categories() -> List[ProductCategory]:
    """Get list of all available categories."""
    return list(ProductCategory)


def get_category_keywords(category: ProductCategory) -> List[str]:
    """Get keywords associated with a category."""
    if category in _classifier.category_keywords:
        return list(_classifier.category_keywords[category].keys())
    return []


def is_valid_category(category_str: str) -> bool:
    """Check if a string represents a valid category."""
    try:
        ProductCategory(category_str.lower().replace(' ', '-'))
        return True
    except ValueError:
        return False


def normalize_category_name(category_str: str) -> str:
    """Normalize category name to standard format."""
    try:
        category = ProductCategory(category_str.lower().replace(' ', '-'))
        return category.value
    except ValueError:
        return ProductCategory.UNKNOWN.value