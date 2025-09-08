import requests
import json



"""## Classes"""

class Matchtype:
  def __init__(self, type):
    self.type = type

  def get_type(self):
    return self.type

  def set_type(self, type):
    self.type = type


class MatchProperty:
  def __init__(self, property):
    self.property = property

  def get_property(self):
    return self.property

  def set_property(self, property):
    self.property = property

class Match:
    def __init__(self, matching_term, match_property, match_type, term_code, vocabulary, concept_uri):
        self._matching_term = matching_term
        self._match_property = match_property
        self._match_type = match_type
        self._term_code = term_code
        self._vocabulary = vocabulary
        self._concept_uri = concept_uri

    def getMatchingTerm(self):
        return self._matching_term

    def getMatchProperty(self):
        return self._match_property

    def getMatchType(self):
        return self._match_type

    def getTermCode(self):
        return self._term_code

    def getVocabulary(self):
        return self._vocabulary

    def getConceptURI(self):
        return self._concept_uri


class SemanticAnalyzer:
  def __init__(self, endpoint="https://semantics.bodc.ac.uk/api/analyse"):
    self.endpoint = endpoint

  def getMatchTypes(self):
    # This method would typically call an endpoint to get valid match types
    # For now, returning a placeholder list
    return [Matchtype("exactMatch")]

  def getMatchProperties(self):
    # This method would typically call an endpoint to get valid match properties
    # For now, returning a placeholder list
    return [MatchProperty("altLabel"), MatchProperty("prefLabel")]

  def analyzeTerms(self, terms: list[str], matchTypes: list[Matchtype], matchProperties: list[MatchProperty]):
    """
    Analyzes a list of terms using the semantic analysis endpoint.

    Args:
      terms: A list of strings representing the terms to analyze.
      matchTypes: A list of Matchtype objects.
      matchProperties: A list of MatchProperty objects.

    Returns:
      A SemanticAnalysisResponse object containing the analysis results.
    """
    payload = {
        "terms": terms,
        "matchTypes": [mt.get_type() for mt in matchTypes],
        "matchProperties": [mp.get_property() for mp in matchProperties]
    }
    headers = {'Content-Type': 'application/json'}

    try:
      response = requests.post(self.endpoint, data=json.dumps(payload), headers=headers)
      response.raise_for_status()  # Raise an exception for bad status codes (4xx or 5xx)
      return SemanticAnalysisResponse(response.json())
    except requests.exceptions.RequestException as e:
      print(f"Error during semantic analysis request: {e}")
      return None



class SemanticAnalysisResponse:
  def __init__(self, data):
    self.data = data
    self._matches = self._parse_matches()

  def get_analysis_results(self):
    return self.data

  def get_matches(self):
      return self._matches

  def _parse_matches(self):
      matches = []
      if self.data and '@graph' in self.data:
          for graph_item in self.data['@graph']:
              if 'result' in graph_item:
                  for result_item in graph_item['result']:
                      # Extract information from the result_item dictionary
                      matching_term = graph_item.get('query', 'N/A')
                      match_property = result_item.get('matchProperty', 'N/A')
                      match_type = result_item.get('matchType', 'N/A')
                      term_code = result_item.get('termCode', 'N/A')
                      # Assuming vocabulary can be extracted from the '@id' or 'inDefinedTermSet'
                      vocabulary = result_item.get('inDefinedTermSet', 'N/A')
                      concept_uri = result_item.get('@id', 'N/A')

                      # Create a Match object and add it to the list
                      match = Match(matching_term, match_property, match_type, term_code, vocabulary, concept_uri)
                      matches.append(match)
      return matches



