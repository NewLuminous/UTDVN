import nltk

class Query(object):
    """
    Allows component-based building and manipulation of Solr query strings.
    Example Usage:
        query = Query(query_str)
        query.select_and(other_query)
        query.select_or(other_query)
        return str(query)
        
        query = Query(doc_id, as_phrase=False, escape=True) \
            .for_single_field('id') \
            .select_or(
                Query(author, as_phrase=False, escape=True) \
                .for_single_field('author') \
                .select_and(
                    Query(title, as_phrase=False, escape=True) \
                        .for_single_field('title')
                )
            )
    """

    def __init__(self, query_str, as_phrase=True, escape=False, sanitize=False):
        """
        Parameters
        ----------
        query_str : string
            The query.
        as_phrase : bool, optional
            Should this query be formatted as a phrase. The default is True.
        escape : bool, optional
            Should special characters be escaped from the phrase. The default is False.
        sanitize : bool, optional
            Should query be stripped of trivial words. The default is False.

        Initializes a Query.
        """
        self.query_str = query_str

        if escape:
            self._escape_special_chars()

        if sanitize:
            self._sanitize()

        if as_phrase:
            self._as_phrase()
            
    def __str__(self):
        """
        Returns query as a string.
        """
        return self.query_str
    
    def select_and(self, query):
        """
        Returns new Query joining this query and another query with an AND select.
        """
        return Query('%s AND %s' % (self.query_str, str(query)), as_phrase=False)

    def select_or(self, query):
        """
        Returns new Query joining this query and another query with an OR select.
        """
        return Query('%s OR %s' % (self.query_str, str(query)), as_phrase=False)

    def select_require(self, terms):
        """
        Returns new Query requiring the given terms.
        """
        if len(terms) == 0:
            return self
        
        new_query_str = self.query_str
        for term in terms:
            new_query_str += '+%s' % term
        return Query(new_query_str, as_phrase=False)
    
    def boost_importance(self, factor):
        """
        Returns new Query raising the importance of the query to given factor.
        """
        return Query('(%s)^%s' % (self.query_str, str(factor)), as_phrase=False)
    
    def for_single_field(self, field):
        """
        Returns new Query that applies given field to the query.
        """
        if field == '':
            return self
        
        return Query('%s:%s' % (field, self.query_str), as_phrase=False)
    
    def for_fields(self, fields):
        """
        Returns new Query that applies given fields to the query.
        """
        if type(fields) is not dict:
            raise ValueError('Fields must be a dictionary of field names and boost factors.')
        
        return Query(self.query_str, as_phrase=False) \
                .select_or(self._for_fields_helper(self.query_str, list(fields.items())))
        
    def _for_fields_helper(self, query_str, fields):
        field, boost = fields[0]
        query = Query(query_str, as_phrase=False) \
                .boost_importance(boost) \
                .for_single_field(field)
                
        if fields[1:]:
            return query.select_or(query._for_fields_helper(query_str, fields[1:]))
        else:
            return query
        
    def fuzz(self, factor):
        '''
        "Fuzzes" the query by a given factor where 0 <= factor <=2.
        Acts differently depending on whether the query is a phrase or not.
        For phrases, this factor determines how far about the words of a phrase can be found.
        For terms, this factor determines how many insertions/deletions will still return a match.
        '''
        if factor < 0 or factor > 2:
            raise ValueError('Factor must be between 0 and 2.')

        return Query('%s~%s' % (self.query_str, factor), as_phrase=False)
    
    def _as_phrase(self):
        '''
        Formats query as entire phrase, and optionally sets proximity for
        words within the phrase.
        '''
        self.query_str = '"%s"' % self.query_str
        
    def _escape_special_chars(self):
        '''
        Escapes special characters that interfere with Solr's query parser.
        Ideally only use on queries where as_phrase=False, 
        since special characters in phrases do not upset Solr.
        '''
        special_chars = ['!', '(', ')', '{', '}', '[', ']', '^', '"', '~', '*', '?', ':', '|', '&']
        for c in special_chars:
            self.query_str = self.query_str.replace(c, '\\'+c)

    def _sanitize(self):
        '''
        Trims nonessential words such as 'and', 'or', 'for'
        Parts of Speech types:
        http://www.ling.upenn.edu/courses/Fall_2003/ling001/penn_treebank_pos.html
        '''
        tags_to_keep = [
            'NN', 'NNS', 'NNP', 'NNPS',       # noun types
            'VB', 'VBG', 'VBN', 'VBP', 'VBZ', # verb types
            'JJ', 'JJR', 'JJS',               # adjective types
            'RB', 'RBR', 'RBS',               # adverbs
        ]
        tokens = nltk.word_tokenize(self.query_str)
        tags = nltk.pos_tag(tokens)
        words_list = []
        for tag in tags:
            if tag[1] in tags_to_keep:
                words_list.append(tag[0])
        new_query_str = ' '.join(words_list)
        self.query_str = new_query_str if len(new_query_str)>0 else self.query_str