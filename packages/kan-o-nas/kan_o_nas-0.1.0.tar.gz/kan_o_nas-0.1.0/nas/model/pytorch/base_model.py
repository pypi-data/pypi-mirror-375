from __future__ import annotations

import timeit
from typing import Union, Optional, Tuple, List, Dict, Any, Sequence

import numpy as np
import torch
import torch.nn
import tqdm
from golem.core.dag.graph_node import GraphNode
from numpy import ndarray, dtype
from torch import nn
from torch.utils.data import DataLoader

from nas.graph.base_graph import NasGraph
from nas.graph.node.nas_graph_node import NasNode
from nas.graph.node.nas_node_params import NasNodeFactory
from nas.model.model_interface import NeuralSearchModel
from nas.model.pytorch.layers.kan_convolutional.KANLinear import KANLinear
from nas.model.pytorch.layers.layer_initializer import TorchLayerFactory
from nas.repository.layer_types_enum import LayersPoolEnum


# from ptflops import get_model_complexity_info


def present_node_dim_info(input_shape, weighted_layer_output_shape, output_shape) -> dict:
    dim_kind = "2d" if len(output_shape) == 3 else "flatten" if len(input_shape) == 3 else "1d"
    res = {
        "dim_kind": dim_kind,
    }

    def present_2d_shape_dim_info(shape) -> dict:
        return {
            "channels": shape[0],
            "side_size": shape[1],  # Only valid if h == w
            "h": shape[1],
            "w": shape[2]
        }

    if dim_kind == "2d":
        res["input"] = present_2d_shape_dim_info(input_shape)
        res["weighted_layer_output_shape"] = present_2d_shape_dim_info(weighted_layer_output_shape)
        res["output"] = present_2d_shape_dim_info(output_shape)

    if dim_kind == "flatten":
        res["input"] = present_2d_shape_dim_info(input_shape)
        res["flattened"] = output_shape[0]
        res["output_dim"] = res["flattened"]  # To keep compatibility with 1d

    if dim_kind == "1d":
        res["input_dim"] = input_shape[0]
        res["output_dim"] = output_shape[0]

    # TODO: cache computational complexity here, too

    return res


def count_parameters(module: nn.Module):
    return sum(p.numel() for p in module.parameters() if p.requires_grad)


def compute_total_graph_parameters(graph: NasGraph, in_shape, out_shape):
    # First, initialize `NASTorchModel` to cache dims/parameters
    m = NeuralSearchModel(NASTorchModel).compile_model(graph, in_shape, out_shape).model
    # all_layer_parameters = sum(n.content["parameter_count"] for n in graph.nodes)
    # print(f"Counted in full model: {count_parameters(m)}")
    # print(f"Computed by layer: {all_layer_parameters}")

    # Compute sum of all node parameters
    return count_parameters(m)


def get_flops_from_graph(graph: NasGraph, in_shape, out_shape) -> int:
    # m = NeuralSearchModel(NASTorchModel).compile_model(graph, in_shape, out_shape).model
    # flop_stat = get_flops_obj_from_model(m, in_shape)
    # # Cache the total number of flops to the flatten node of the graph:
    # flatten_node = graph.get_singleton_node_by_name('flatten')
    # flatten_node.content["total_model_flops"] = flop_stat
    # # Also set flops by layer type:
    # flatten_node.content["flops_by_layer"] = {}
    # for k, v in flop_stat.by_operator().items():
    #     flatten_node.content["flops_by_layer"][k] = v
    return 0


def get_flops_obj_from_model(model: nn.Module, in_shape) -> int:
    # input = torch.rand([2, *in_shape[::-1]])
    # flops = FlopCountAnalysis(model, input)
    # macs, params = get_model_complexity_info(model, tuple(input.shape), as_strings=True, backend='pytorch',
    #                                          print_per_layer_stat=True, verbose=True)
    # print('{:<30}  {:<8}'.format('Computational complexity: ', macs))
    # print('{:<30}  {:<8}'.format('Number of parameters: ', params))

    # macs, params = get_model_complexity_info(model, tuple(input.shape[1:]), as_strings=False, backend='aten',
    #                                          print_per_layer_stat=False, verbose=False)
    # print('{:<30}  {:<8}'.format('Computational complexity: ', macs))
    # print('{:<30}  {:<8}'.format('Number of parameters: ', params))

    # print(flops.by_module())
    # print(flops.by_operator())
    # for k, v in flops.by_operator().items():
    #     print(k, v)
    # print(flops.by_module_and_operator())

    return 0


def get_time_from_graph(graph: NasGraph, in_shape, out_shape, device, optimization_batch_size) -> float:
    batch_size = 2 if device == 'cpu' else optimization_batch_size
    model = NeuralSearchModel(NASTorchModel).compile_model(graph, in_shape, out_shape).model.to(device)
    example_input = torch.rand([batch_size, *in_shape[::-1]]).to(device)

    res = timeit.timeit(lambda: model(example_input), number=10)
    # print("time: ", res)
    return res


class NASTorchModel(torch.nn.Module):
    """
    Makes torch Module from a graph representing model's data flow.
    """

    def __init__(self, **kwargs):
        super().__init__()
        self.model_layers = None
        self.output_layer = None

        self._graph = None

    def set_device(self, device):
        self.to(device)

    @property
    def is_cls(self):
        return not self.is_ts

    def init_model(self, in_shape: Union[Tuple[int], List[int]], out_shape: Optional[int, Sequence[int]],
                   graph: NasGraph, **kwargs):
        self.is_ts = isinstance(out_shape, Sequence)  # Time series forecasting
        preprocess_graph_for_imagenet = kwargs.get('preprocess_graph_for_imagenet', False)
        if preprocess_graph_for_imagenet:
            # Preprocess for ImageNet:
            flatten = graph.root_node
            assert flatten.name == "flatten"
            assert len(graph.root_node.nodes_from) == 1
            last_conv = graph.root_node.nodes_from[0]
            graph.disconnect_nodes(last_conv, flatten)

            pool_type = LayersPoolEnum.pooling2d
            # ada_pooling_node_params = NasNodeFactory().get_node_params(ada_pool_type, out_shape=(4, 4), mode="average")
            pooling_node_params = NasNodeFactory().get_node_params(pool_type, pool_size=(2, 2), pool_stride=(2, 2),
                                                                   mode="average")
            pooling_node = NasNode(content={'name': pool_type.value, 'params': pooling_node_params},
                                   nodes_from=[last_conv])
            graph.add_node(pooling_node)
            graph.connect_nodes(pooling_node, flatten)

        self._graph = graph

        visited_nodes = set()
        visited_node_outputs = {}
        if self.is_cls:
            out_shape = out_shape if out_shape > 2 else 1

        def _init_layer(node: Union[GraphNode, NasNode]) -> torch.Tensor:
            if node.nodes_from:
                for n in node.nodes_from:
                    input_tensor = _init_layer(n)
            else:
                input_tensor = torch.rand([2, *in_shape[::-1]])

            if node not in visited_nodes:
                layer_func = TorchLayerFactory.get_layer(node)
                input_channels = input_tensor.shape[1]
                layer = layer_func['weighted_layer'](node, input_dim=input_channels)

                # Cache parameter data:
                node.content["parameter_count"] = count_parameters(layer)
                weighted_layer_output_tensor = layer(input_tensor)
                current_output_tensor = weighted_layer_output_tensor

                self.__setattr__(f'node_{node.uid}', layer)
                if layer_func.get('normalization'):
                    output_shape = node.parameters['out_shape']
                    normalization_module = layer_func['normalization'](node, input_dim=output_shape)
                    self.__setattr__(f'node_{node.uid}_n', normalization_module)
                    node.content["parameter_count"] += count_parameters(normalization_module)
                    current_output_tensor = normalization_module(current_output_tensor)

                if layer_func.get('pooling'):
                    output_shape = node.parameters['out_shape']  # Normalization preserves output shape
                    pooling_module = layer_func['pooling'](node, input_dim=output_shape)
                    self.__setattr__(f'node_{node.uid}_p', pooling_module)
                    node.content["parameter_count"] += count_parameters(pooling_module)
                    current_output_tensor = pooling_module(current_output_tensor)

                # Cache dims data:
                input_shape = input_tensor.shape[1:]
                output_shape = current_output_tensor.shape[1:]
                weighted_layer_output_shape = weighted_layer_output_tensor.shape[1:]
                node.content["dims"] = present_node_dim_info(input_shape, weighted_layer_output_shape, output_shape)

                visited_node_outputs[node.uid] = current_output_tensor
                visited_nodes.add(node)

            return visited_node_outputs[node.uid]

        _init_layer(graph.root_node)

        # Use root node to extract output layer parameters (a dirty hack)
        # All nodes have this parameter in KAN case but only for the root they are applied
        if self.is_cls:
            node_with_output_parameters = graph.get_input_node()
            if "kan" in node_with_output_parameters.name:
                # It's a parameters for KAN output node → mode is KAN
                grid_size = node_with_output_parameters.parameters["output_node_grid_size"]
                spline_order = node_with_output_parameters.parameters["output_node_spline_order"]
                self.output_layer = KANLinear(
                    in_features=graph.root_node.content["dims"]["output_dim"],
                    out_features=out_shape,
                    grid_size=grid_size,
                    spline_order=spline_order
                )
            else:
                self.output_layer = torch.nn.Linear(graph.root_node.content["dims"]["output_dim"], out_shape)

            # Cache the total number of parameters to the flatten node of the graph:
            flatten_node = self._graph.get_singleton_node_by_name('flatten')
            flatten_node.content["total_model_parameter_count"] = count_parameters(self)

            # if preprocess_graph_for_imagenet:
            # last_conv = flatten_node.nodes_from[0]
            # print("Last Conv parameters:", last_conv.content)

            # Cache the total number of flops to the flatten node of the graph:
            # flop_stat = get_flops_obj_from_model(self, in_shape)
            # flatten_node.content["total_model_flops"] = flop_stat.total()
            # # Also set flops by layer type:
            # flatten_node.content["flops_by_layer"] = {}
            # for k, v in flop_stat.by_operator().items():
            #     flatten_node.content["flops_by_layer"][k] = v

    def forward(self, inputs: torch.Tensor):
        visited_nodes = set()
        node_to_save = dict()

        def _forward_pass_one_layer_recursive(node: Union[GraphNode, NasNode]):
            layer_name = f'node_{node.uid}'
            layer_state_dict = self.__getattr__(layer_name)
            if node in visited_nodes:
                node_to_save[node]['calls'] -= 1
                cond2remove = node_to_save[node]['calls'] == 1
                output = node_to_save[node]['output']
                if cond2remove:
                    del node_to_save[node]
                return output
            first_save_cond = len(self._graph.node_children(node)) > 1 or len(node.nodes_from) > 1
            second_save_cond = node not in node_to_save.keys()
            if first_save_cond and second_save_cond:
                node_to_save[node] = None
            layer_inputs = [_forward_pass_one_layer_recursive(parent) for parent in node.nodes_from] \
                if node.nodes_from else [inputs]
            output = layer_state_dict(layer_inputs[0])
            for supplementary_module in [f'{layer_name}_n', f'{layer_name}_p']:
                if hasattr(self, supplementary_module):
                    output = self.__getattr__(supplementary_module)(output)
            if len(node.nodes_from) > 1:
                shortcut = layer_inputs[-1]
                output += shortcut
            if node.name not in ['pooling2d', 'dropout', 'adaptive_pool2d', 'flatten', 'kan_conv2d', 'kan_linear']:
                output = TorchLayerFactory.get_activation(node.parameters['activation'])()(output)
            if node in node_to_save.keys():
                node_to_save[node] = {'output': output,
                                      'calls': len(self._graph.node_children(node))}
            visited_nodes.add(node)
            return output

        out = _forward_pass_one_layer_recursive(self._graph.root_node)
        del node_to_save
        return self.output_layer(out) if self.is_cls else out

    def _one_epoch_train(self, train_data: DataLoader, optimizer, loss_fn, device, epoch_index=None):
        running_loss = 0
        disable_debug_info = False
        pbar = tqdm.trange(len(train_data), desc='Batches of epoch' + str(epoch_index), leave=False, position=0,
                           disable=disable_debug_info
                           )
        # for b in range():
        #     pass
        # print(train_data.[0].shape)
        losses = []
        for batch_id, (features_batch, targets_batch) in enumerate(train_data):
            pbar.update()
            features_batch, targets_batch = features_batch.to(device), targets_batch.to(device)
            optimizer.zero_grad()
            outputs = self.__call__(features_batch)
            loss = loss_fn(outputs, targets_batch)
            loss.backward()
            optimizer.step()
            l = loss.detach().cpu().item()
            running_loss += l
            losses.append(l)
            if not disable_debug_info and batch_id % 100 == 0:
                to_compute_loss = losses[-100:]
                print("Running loss:", torch.tensor(to_compute_loss).mean().item())
        pbar.close()
        running_loss = running_loss / len(train_data)
        return running_loss

    def validate(self, val_data: DataLoader, loss_fn, device, **kwargs) -> Dict:
        self.eval()
        self.set_device(device)
        metrics_to_calc = kwargs.get('metrics')
        # Would do if there weren't cpu←—→gpu transitions
        # if metrics_to_calc is None:
        #     metrics_to_calc = {"loss": loss_fn}

        metrics = {'val_loss': 0}

        for batch_id, (features_batch, targets_batch) in enumerate(val_data):
            features_batch, targets_batch = features_batch.to(device), targets_batch.to(device)
            outputs = self.__call__(features_batch)
            major_outputs = torch.argmax(outputs, dim=-1)  # Softmax is omitted
            loss = loss_fn(outputs, targets_batch)
            # if metrics_to_calc is None:
            metrics['val_loss'] += loss.detach().cpu().item()
            if metrics_to_calc:
                for metric_name, metric_func in metrics_to_calc.items():
                    if metrics.get(f'val_{metric_name}') is None:
                        metrics[f'val_{metric_name}'] = 0
                    metrics[f'val_{metric_name}'] += metric_func(major_outputs.detach().cpu().numpy(),
                                                                 torch.argmax(targets_batch,
                                                                              dim=-1).detach().cpu().numpy())

        metrics = {key: val / len(val_data) for key, val in metrics.items()}
        print("Validation metrics calculated:", metrics)
        return metrics

    def fit(self, train_data: DataLoader,
            loss,
            val_data: Optional[DataLoader] = None,
            optimizer=torch.optim.AdamW,
            epochs: int = 1,
            device: str = 'cpu',
            timeout_seconds: Optional[int] = None,
            **kwargs):
        """
        This function trains the pytorch module using given parameters
        """
        self.set_device(device)
        metrics_to_val = kwargs.get('metrics')
        metrics = dict()
        optim = optimizer(self.parameters(), lr=kwargs.get('lr', 1e-3), weight_decay=5e-6)
        pbar = tqdm.trange(epochs, desc='Fitting graph', leave=False, position=0)
        start_time = timeit.default_timer()
        last_save = start_time
        for epoch in pbar:
            self.train(mode=True)
            train_loss = self._one_epoch_train(train_data, optim, loss, device, epoch_index=epoch)
            metrics['train_loss'] = train_loss
            if val_data:
                with torch.no_grad():
                    self.eval()
                    val_metrics = self.validate(val_data, loss, device, metrics=metrics_to_val)
                    self.train()
                metrics.update(val_metrics)
            print(f"Epoch: {epoch}, Current metrics: {metrics}")
            time_elapsed = timeit.default_timer() - start_time
            if time_elapsed - last_save > 60 * 5:
                last_save = time_elapsed
                self.save_model(f"model_weights.pth")
            if timeout_seconds and time_elapsed > timeout_seconds:
                break

    def predict(self,
                test_data: DataLoader,
                device: str = 'cpu') -> Tuple[ndarray[Any, dtype[Any]], ndarray[Any, dtype[Any]]]:
        """
        This method implements prediction on data loader.
        Returns tuple of predicted probabilities and target labels.
        """
        self.set_device(device)
        self.eval()
        results = []
        targets_lst = []
        activation = torch.nn.Softmax(-1)
        with torch.no_grad():
            for features, targets in test_data:
                features, targets = features.to(device), targets.to(device)
                predictions = self.__call__(features)
                if self.is_cls:
                    results.extend(activation(predictions).detach().cpu().tolist())
                    targets_lst.extend(torch.argmax(targets, dim=-1).detach().cpu().tolist())
                else:  # ts
                    results.extend(predictions.detach().cpu().numpy())
                    targets_lst.extend(targets.detach().cpu().numpy())
        return np.array(results), np.array(targets_lst)

    def save_model(self, path: str):
        torch.save(self.state_dict(), path)
