import cPickle as pickle
from constr import constr

X, y, X_test, y_test, features_map = constr(segment='income_high', files_n=47,
                                            lower_pop_bound=2,
                                            ngram_ns=[1, 2], min_word_length=1, word_type='alphanumeric',
                                            use_urls=True, min_url_depth=1)

pickle.dump((X, y, X_test, y_test, features_map), open('prepared/income_high_allegedly_best.pickle', 'wb'), -1)