import gc
import torch
from golem.core.log import default_log
from golem.core.optimisers.fitness import Fitness, SingleObjFitness, MultiObjFitness
from golem.core.optimisers.objective import ObjectiveEvaluate, Objective
from golem.core.optimisers.objective.objective import to_fitness
from torch.utils.data import DataLoader, Dataset
from nas.utils.random_split_hack import random_split

from nas.composer.requirements import NNComposerRequirements
from nas.graph.base_graph import NasGraph
from nas.model.constructor import ModelConstructor
from nas.model.model_interface import NeuralSearchModel


class NASObjectiveEvaluate(ObjectiveEvaluate):
    """
    This class defines how Objective will be evaluated for neural network like graph structure.
    """

    def __init__(self,
                 objective: Objective,
                 train_dataset: Dataset,
                 validation_dataset: Dataset,
                 model_trainer_builder: ModelConstructor,
                 requirements: NNComposerRequirements,
                 verbose_level=None,
                 eval_n_jobs: int = 1,
                 dataloader_num_workers: int = 1,
                 **objective_kwargs):
        super().__init__(objective=objective, eval_n_jobs=eval_n_jobs, **objective_kwargs)
        self.verbose_level = verbose_level
        # self._data_producer = data_producer
        # self._dataset_builder = nn_dataset_builder
        self._train_dataset = train_dataset
        self._validation_dataset = validation_dataset
        self._model_trainer_builder = model_trainer_builder
        self._requirements = requirements
        self._log = default_log(self)
        self._dataloader_num_workers = dataloader_num_workers

    def evaluate(self, graph: NasGraph) -> Fitness:
        # return MultiObjFitness([random.random(), list(self._objective.metrics)[-1][1](graph)])
        # train_data, test_data = random_split(self._dataset, [.8, .2])
        gc.collect()
        torch.cuda.empty_cache()
        fitted_model = self._graph_fit(graph, self._train_dataset, log=self._log, debug_test_data=self._validation_dataset)
        fold_fitness = self._evaluate_fitted_model(fitted_model, self._validation_dataset, graph, log=self._log)
        del fitted_model
        return fold_fitness

    def _graph_fit(self, graph: NasGraph, train_data: Dataset, log, debug_test_data: Dataset) -> NeuralSearchModel:
        """
        This method compiles and fits a neural network based on given parameters and graph structure.

        Args:
             graph - Graph with defined search space of operations to apply during training process;
             train_data - dataset used as an entry point into the pipeline fitting procedure;

         Returns:
             Fitted model object
        """
        shuffle_flag = True
        # classes = self._requirements.model_requirements.num_of_classes
        batch_size = self._requirements.model_requirements.batch_size
        opt_epochs = self._requirements.opt_epochs

        # opt_data, val_data = train_test_data_setup(train_data, stratify=train_data.target)
        opt_dataset = DataLoader(train_data, batch_size=batch_size, shuffle=shuffle_flag, num_workers=self._dataloader_num_workers)
        # val_dataset = DataLoader(self._dataset_builder.build(val_data), batch_size=batch_size, shuffle=shuffle_flag)

        input_shape = self._requirements.model_requirements.input_shape
        output_shape = self._requirements.model_requirements.output_shape
        trainer = self._model_trainer_builder.build(input_shape=input_shape, output_shape=output_shape, graph=graph)
        # NOTE: COMMENT OUT TO SKIP TRAINING IN DEBUG PURPOSES
        trainer.fit_model(train_data=opt_dataset,
                          # val_data=debug_test_data,
                          timeout_seconds=self._requirements.optimization_fitting_timeout_seconds,
                          epochs=opt_epochs)
        return trainer

    def _evaluate_fitted_model(self, fitted_model: NeuralSearchModel, test_data: Dataset, graph: NasGraph,
                               log):
        """
        Method for graph's fitness estimation on given data. Estimates fitted model fitness.
        """
        # complexity_metrics = [m(graph) for _, m in self._objective.complexity_metrics.items()]
        # complexity_metrics.extend([m(graph) for m in self._objective.quality_metrics[1:].values()])
        complexity_metrics = [m(graph) for _, m in
                              self._objective.metrics[1:]]  # dicts maintain insertion order, first is loss
        test_dataset = DataLoader(test_data,
                                  batch_size=self._requirements.model_requirements.batch_size,
                                  shuffle=False, num_workers=self._dataloader_num_workers)
        eval_metrics = fitted_model.validate(test_dataset)
        # Hm, just done eval_metrics["val_loss"] in the other branch? Why did I do so?
        eval_metrics = [m for m in eval_metrics.values()]
        return to_fitness([*eval_metrics, *complexity_metrics], self._objective.is_multi_objective)
