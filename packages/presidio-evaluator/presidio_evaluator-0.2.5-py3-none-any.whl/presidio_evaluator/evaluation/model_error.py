from enum import Enum
from typing import Dict, List, Optional, Union
from pprint import pprint

import pandas as pd
from spacy.tokens import Token


class ErrorType(Enum):
    """Enum for which type of error a ModelError is.

    Note:
    - False Positives (FPs) are defined as tokens that were predicted as entities,
    but were not annotated as any entity (i.e. "O").
    - False Negatives (FNs) are defined as tokens that were annotated as entities,
    but were predicted as not an entity (i.e. "O").
    - Wrong Entities are defined as tokens that were predicted as one entity,
    but were annotated as a different entity.
    """

    FP = "FP"  # False Positive
    FN = "FN"  # False Negative
    WrongEntity = "WrongEntity"  # Wrong entity type


class ModelError:
    def __init__(
        self,
        error_type: Union[str, ErrorType],
        annotation: str,
        prediction: str,
        token: Optional[Union[Token, str]] = None,
        full_text: Optional[str] = None,
        sample_id: Optional[int] = None,
        metadata: Optional[Dict] = None,
        explanation: Optional[str] = None,
    ):
        """
        Holds information about an error a model made for analysis purposes
        :param error_type: str, e.g. FP, FN, WrongEntity
        :param annotation: ground truth value
        :param prediction: predicted value
        :param token: token in question
        :param full_text: full input text
        :param sample_id: Id of the sample this error belongs to
        :param metadata: metadata on text from InputSample
        :param explanation: Optional reasoning for the error, e.g. "Token was too short"
        """

        self.error_type = error_type
        self.annotation = annotation
        self.prediction = prediction
        self.token = token.text if isinstance(token, Token) else token
        self.full_text = full_text
        self.sample_id = sample_id
        self.metadata = metadata
        self.explanation = explanation

    def __str__(self):
        return (
            "type: {}, "
            "Annotation = {}, "
            "prediction = {}, "
            "Token = {}, "
            "Full text = {}, "
            "Metadata = {}".format(
                self.error_type,
                self.annotation,
                self.prediction,
                self.token,
                self.full_text,
                self.metadata,
            )
        )

    def __repr__(self):
        return f"<ModelError {self.__str__()}"

    @staticmethod
    def most_common_fp_tokens(
        errors: List["ModelError"], n: int = 10, entity: Optional[str] = None
    ):
        """
        Print the n most common false positive tokens
        (tokens thought to be an entity)
        """
        fps = ModelError.get_false_positives(errors, entity)

        tokens = [err.token for err in fps]
        from collections import Counter

        by_frequency = Counter(tokens)
        most_common = by_frequency.most_common(n)

        print("Most common false positive tokens:")
        pprint(most_common)
        print("---------------")
        print("Example sentence with each FP token:")
        for tok, val in most_common:
            with_tok = [err for err in fps if err.token == tok]
            print(
                f"\t- {with_tok[0].full_text} (`{with_tok[0].token}` "
                f"pred as {with_tok[0].prediction})"
            )

        return most_common

    @staticmethod
    def most_common_fn_tokens(
        errors: List["ModelError"], n: int = 10, entity: Optional[str] = None
    ):
        """
        Print all tokens that were missed by the model,
        including an example of the full text in which they appear.
        """
        fns = ModelError.get_false_negatives(errors, entity)

        fns_tokens = [err.token for err in fns]
        from collections import Counter

        by_frequency_fns = Counter(fns_tokens)
        most_common_fns = by_frequency_fns.most_common(n)
        print("Most common false negative tokens:")
        pprint(most_common_fns)
        print("---------------")
        print("Example sentence with each FN token:")
        for tok, val in most_common_fns:
            with_tok = [err for err in fns if err.token == tok]
            print(
                f"\t- {with_tok[0].full_text} (`{with_tok[0].token}` "
                f"annotated as {with_tok[0].annotation})"
            )

        return most_common_fns

    @staticmethod
    def get_errors_df(
        errors: List["ModelError"],
        error_type: ErrorType,
        entity: Optional[str] = None,
        verbose: bool = True,
    ) -> Optional[pd.DataFrame]:
        """
        Get ModelErrors as pd.DataFrame
        :param errors: A list of ModelErrors
        :param error_type: Should be either FP, FN or WrongEntity
        :param entity: Entity to filter on
        :param verbose: True if should print
        """
        wrong_fp = ModelError.get_wrong_entities(errors, predicted_entity=entity)
        wrong_fn = ModelError.get_wrong_entities(errors, annotated_entity=entity)

        if error_type == ErrorType.FN:
            filtered_errors = ModelError.get_false_negatives(errors, entity) + wrong_fn
        elif error_type == ErrorType.FP:
            filtered_errors = ModelError.get_false_positives(errors, entity) + wrong_fp
        elif error_type == ErrorType.WrongEntity:
            filtered_errors = wrong_fp + wrong_fn
        else:
            raise ValueError("error_type should be either FP, FN or `WrongEntity`")

        if len(filtered_errors) == 0:
            if verbose:
                print(f"No errors of type {error_type} and entity {entity} were found")
            return None

        errors_df = pd.DataFrame.from_records(
            [error.__dict__ for error in filtered_errors]
        )
        metadata_df = pd.DataFrame(errors_df["metadata"].tolist())
        errors_df.drop(["metadata"], axis=1, inplace=True)
        new_errors_df = pd.concat([errors_df, metadata_df], axis=1)
        return new_errors_df

    @staticmethod
    def get_fps_dataframe(
        errors: List["ModelError"], entity: Optional[str] = None, verbose: bool = True
    ) -> pd.DataFrame:
        """
        Get false positive ModelErrors as pd.DataFrame
        """
        return ModelError.get_errors_df(
            errors=errors, error_type=ErrorType.FP, entity=entity, verbose=verbose
        )

    @staticmethod
    def get_fns_dataframe(
        errors: List["ModelError"], entity: Optional[str] = None, verbose: bool = True
    ) -> pd.DataFrame:
        """
        Get false negative ModelErrors as pd.DataFrame
        """
        return ModelError.get_errors_df(
            errors=errors, error_type=ErrorType.FN, entity=entity, verbose=verbose
        )

    @staticmethod
    def get_wrong_entity_dataframe(
        errors: List["ModelError"], entity: Optional[str] = None, verbose: bool = True
    ) -> pd.DataFrame:
        """
        Get wrong entity ModelErrors as pd.DataFrame
        """
        return ModelError.get_errors_df(
            errors=errors,
            error_type=ErrorType.WrongEntity,
            entity=entity,
            verbose=verbose,
        )

    @staticmethod
    def __get_error_of_type(
        errors: List["ModelError"], error_type: ErrorType, entity: Optional[str] = None
    ) -> List["ModelError"]:
        """
        Get a list of all errors of a specific type in the results
        """
        subset = [
            model_error
            for model_error in errors
            if model_error.error_type == error_type
        ]
        if entity:
            if error_type == ErrorType.FP:
                return [
                    model_error
                    for model_error in subset
                    if model_error.prediction in entity
                ]
            else:
                return [
                    model_error
                    for model_error in subset
                    if model_error.annotation in entity
                ]
        else:
            return subset

    @staticmethod
    def get_false_positives(
        errors: List["ModelError"], entity: Optional[str] = None
    ) -> List["ModelError"]:
        """
        Get a list of all false positive errors in the results
        """
        fps = ModelError.__get_error_of_type(errors, ErrorType.FP, entity)
        wrong = ModelError.get_wrong_entities(errors, predicted_entity=entity)
        return fps + wrong

    @staticmethod
    def get_false_negatives(
        errors: List["ModelError"], entity: Optional[str] = None
    ) -> List["ModelError"]:
        """
        Get a list of all false negative errors in the results
        """

        fns = ModelError.__get_error_of_type(errors, ErrorType.FN, entity)
        wrong = ModelError.get_wrong_entities(errors, annotated_entity=entity)
        return fns + wrong

    @staticmethod
    def get_wrong_entities(
        errors: List["ModelError"],
        annotated_entity: Optional[str] = None,
        predicted_entity: Optional[str] = None,
    ) -> List["ModelError"]:
        """
        Get a list of all mismatches in the results
        (wrongEntity detection)
        """

        wrong_entities_errors = [
            model_error
            for model_error in errors
            if model_error.error_type == ErrorType.WrongEntity
        ]

        if annotated_entity:
            return [
                model_error
                for model_error in wrong_entities_errors
                if (model_error.annotation in annotated_entity)
            ]
        elif predicted_entity:
            return [
                model_error
                for model_error in wrong_entities_errors
                if (model_error.prediction in predicted_entity)
            ]
        else:
            return wrong_entities_errors
