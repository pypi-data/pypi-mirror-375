import re
import keras
import numpy as np
import tensorflow as tf
import tensorflow_text as tf_text
from rdkit import Chem

from molcraft import ops
from molcraft import chem 
from molcraft import features 
from molcraft import featurizers
from molcraft import tensors
from molcraft import descriptors
from molcraft import layers
from molcraft import models 



@keras.saving.register_keras_serializable(package='molcraft')
class SequenceSplitter(keras.layers.Layer):

    _pattern = "|".join([
        r'(\[[A-Za-z0-9]+\]-[A-Z]\[[A-Za-z0-9]+\])', # N-term mod + mod
        r'([A-Z]\[[A-Za-z0-9]+\]-\[[A-Za-z0-9]+\])', # C-term mod + mod
        r'([A-Z]-\[[A-Za-z0-9]+\])', # C-term mod
        r'(\[[A-Za-z0-9]+\]-[A-Z])', # N-term mod
        r'([A-Z]\[[A-Za-z0-9]+\])', # Mod
        r'([A-Z])', # No mod
    ])

    def call(self, inputs):
        inputs = tf_text.regex_split(inputs, self._pattern, self._pattern)
        inputs = keras.ops.concatenate([
            tf.strings.join([inputs[:, :-1], '-[X]']),
            inputs[:, -1:]
        ], axis=1)
        return inputs.to_tensor()

@keras.saving.register_keras_serializable(package='molcraft')
class Gather(keras.layers.Layer):

    def __init__(
        self, 
        padding: list[tuple[int]] | tuple[int] | int = 1, 
        mask_value: int = 0,
        **kwargs
    ) -> None:
        super().__init__(**kwargs)
        self._splitter = SequenceSplitter()
        self.padding = padding
        self.mask_value = mask_value
        self.supports_masking = True

        self._tags = list(sorted(residues.keys()))
        self._mapping = tf.lookup.StaticHashTable(
            tf.lookup.KeyValueTensorInitializer(
                keys=self._tags,
                values=range(len(self._tags)),
            ),
            default_value=-1,
        )

    def get_config(self):
        config = super().get_config()
        config['mask_value'] = self.mask_value 
        config['padding'] = self.padding
        return config 

    def call(self, inputs) -> tf.Tensor:
        embedding, sequence = inputs
        sequence = self._splitter(sequence)
        sequence = self._mapping.lookup(sequence)
        readout = ops.gather(embedding, keras.ops.where(sequence == -1, 0, sequence)) 
        readout = keras.ops.where(sequence[..., None] == -1, 0.0, readout)
        return readout

    def compute_mask(
        self, 
        inputs: tensors.GraphTensor, 
        mask: bool | None = None
    ) -> tf.Tensor | None:
        # if self.mask_value is None:
        #     return None
        _, sequence = inputs
        sequence = self._splitter(sequence)
        return keras.ops.not_equal(sequence, '')


@keras.saving.register_keras_serializable(package='molcraft')
class Embedding(keras.layers.Layer):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        tags = list(sorted(residues.keys()))
        self.mapping = tf.lookup.StaticHashTable(
            tf.lookup.KeyValueTensorInitializer(
                keys=tags,
                values=range(len(tags)),
            ),
            default_value=-1,
        )
        self.splitting = SequenceSplitter()
        featurizer = featurizers.MolGraphFeaturizer(super_atom=True)
        tensor_list = [featurizer(residues[tag]) for tag in tags]
        graph = tf.stack(tensor_list, axis=0)
        self._build_on_init(graph)
        self.embedder = models.GraphModel.from_layers(
            [
                layers.Input(graph.spec),
                layers.NodeEmbedding(128),
                layers.EdgeEmbedding(128),
                layers.GraphTransformer(128),
                layers.Readout()
            ]
        )
        self.embedding = tf.Variable(
            initial_value=tf.zeros((114, 128)), trainable=True
        )
        self.new_state = tf.Variable(True, dtype=tf.bool, trainable=False)
        self.gather = Gather()
        self.update_state()

        # Keep AA as is (most simple?), add positional embedding to distingusih N-, C- and non-terminal

    def update_state(self, inputs=None):
        graph = self._graph_tensor
        graph = tensors.to_dict(graph)
        embedding = self.embedder(graph)
        self.embedding.assign(embedding)
        tf.print("STATE UPDATED")
        return embedding

    def call(self, inputs=None, training=None) -> tensors.GraphTensor:
        if training:
            embedding = self.update_state()
            self.new_state.assign(True)
            return self.gather([embedding, inputs])
        else:
            embedding = tf.cond(
                pred=self.new_state,
                true_fn=lambda: self.update_state(),
                false_fn=lambda: self.embedding
            )   
            self.new_state.assign(False)
            return self.gather([embedding, inputs])
    
    def build(self, input_shape):
        super().build(input_shape)

    def _build_on_init(self, x):

        if isinstance(x, tensors.GraphTensor):
            tensor = tensors.to_dict(x)
            self._spec = tf.nest.map_structure(
                tf.type_spec_from_value, tensor
            )
        else:
            self._spec = x

        self._graph = tf.nest.map_structure(
            lambda s: self.add_weight(
                shape=s.shape, 
                dtype=s.dtype, 
                trainable=False,
                initializer='zeros'
            ),
            self._spec
        )

        if isinstance(x, tensors.GraphTensor):
            tf.nest.map_structure(
                lambda v, x: v.assign(x),
                self._graph, tensor
            )

        graph = tf.nest.map_structure(
            keras.ops.convert_to_tensor, self._graph
        )
        self._graph_tensor = tensors.from_dict(graph)

    # def get_config(self) -> dict:
    #     config = super().get_config()
    #     spec = keras.saving.serialize_keras_object(self._spec)
    #     config['spec'] = spec
    #     #config['layers'] = keras.saving.serialize_keras_object(self.embedding.layers)
    #     return config 
    
    # @classmethod
    # def from_config(cls, config: dict) -> 'SequenceToGraph':
    #     spec = config.pop('spec')
    #     spec = keras.saving.deserialize_keras_object(spec)
    #    # config['layers'] = keras.saving.deserialize_keras_object(config['layers'])
    #     layer = cls(**config)
    #     layer._build_on_init(spec)
    #     return layer


@keras.saving.register_keras_serializable(package='molcraft')
class SequenceToGraph(keras.layers.Layer):

    def __init__(
        self, 
        atom_features: list[features.Feature] | str | None = 'auto',
        bond_features: list[features.Feature] | str | None = 'auto',
        molecule_features: list[descriptors.Descriptor] | str | None = 'auto',
        super_atom: bool = True,
        radius: int | float | None = None,
        self_loops: bool = False,
        include_hs: bool = False,
        **kwargs,
    ):
        super().__init__(**kwargs)
        self._splitter = SequenceSplitter()
        featurizer = featurizers.MolGraphFeaturizer(
            atom_features=atom_features,
            bond_features=bond_features,
            molecule_features=molecule_features,
            super_atom=super_atom,
            radius=radius,
            self_loops=self_loops,
            include_hs=include_hs,
            **kwargs,
        )
        tensor_list: list[tensors.GraphTensor] = [
            featurizer(residues[tag]).update({'context': {'tag': tag}}) for tag in residues
        ]
        graph = tf.stack(tensor_list, axis=0)
        self._build_on_init(graph)

    def call(self, sequence: tf.Tensor) -> tensors.GraphTensor:
        sequence = self._splitter(sequence)
        indices = self._tag_to_index.lookup(sequence)
        indices = tf.sort(tf.unique(tf.reshape(indices, [-1]))[0])[1:]
        graph = self._graph_tensor[indices]
        return tensors.to_dict(graph)

    def _build_on_init(self, x):

        if isinstance(x, tensors.GraphTensor):
            tensor = tensors.to_dict(x)
            self._spec = tf.nest.map_structure(
                tf.type_spec_from_value, tensor
            )
        else:
            self._spec = x

        self._graph = tf.nest.map_structure(
            lambda s: self.add_weight(
                shape=s.shape, 
                dtype=s.dtype, 
                trainable=False,
                initializer='zeros'
            ),
            self._spec
        )

        if isinstance(x, tensors.GraphTensor):
            tf.nest.map_structure(
                lambda v, x: v.assign(x),
                self._graph, tensor
            )

        graph = tf.nest.map_structure(
            keras.ops.convert_to_tensor, self._graph
        )
        self._graph_tensor = tensors.from_dict(graph)

        tags = self._graph_tensor.context['tag']

        self._tag_to_index = tf.lookup.StaticHashTable(
            tf.lookup.KeyValueTensorInitializer(
                keys=tags,
                values=range(len(tags)),
            ),
            default_value=-1,
        )

    def get_config(self) -> dict:
        config = super().get_config()
        spec = keras.saving.serialize_keras_object(self._spec)
        config['spec'] = spec
        return config 
    
    @classmethod
    def from_config(cls, config: dict) -> 'SequenceToGraph':
        spec = config.pop('spec')
        spec = keras.saving.deserialize_keras_object(spec)
        layer = cls(**config)
        layer._build_on_init(spec)
        return layer

    # @property 
    # def graph(self) -> tensors.GraphTensor:
    #     return self._graph_tensor
    

@keras.saving.register_keras_serializable(package='molcraft')
class GraphToSequence(keras.layers.Layer):

    def __init__(
        self, 
        padding: list[tuple[int]] | tuple[int] | int = 1, 
        mask_value: int = 0,
        **kwargs
    ) -> None:
        super().__init__(**kwargs)
        self._splitter = SequenceSplitter()
        self.padding = padding
        self.mask_value = mask_value
        self._readout_layer = layers.Readout(mode='mean')
        self.supports_masking = True

    def get_config(self):
        config = super().get_config()
        config['mask_value'] = self.mask_value 
        config['padding'] = self.padding
        return config 

    def call(self, inputs) -> tf.Tensor:

        graph, sequence = inputs
        sequence = self._splitter(sequence)
        tag = graph['context']['tag']
        data = self._readout_layer(graph)

        table = tf.lookup.experimental.MutableHashTable(
            key_dtype=tf.string,
            value_dtype=tf.int32,
            default_value=-1
        )

        table.insert(tag, tf.range(tf.shape(tag)[0]))
        sequence = table.lookup(sequence)

        readout = ops.gather(data, keras.ops.where(sequence == -1, 0, sequence)) 
        readout = keras.ops.where(sequence[..., None] == -1, 0.0, readout)
        return readout

    def compute_mask(
        self, 
        inputs: tensors.GraphTensor, 
        mask: bool | None = None
    ) -> tf.Tensor | None:
        # if self.mask_value is None:
        #     return None
        _, sequence = inputs
        sequence = self._splitter(sequence)
        return keras.ops.not_equal(sequence, '')


residues = {
    "A": "N[C@@H](C)C(=O)O",
    "C": "N[C@@H](CS)C(=O)O",
    "C[Carbamidomethyl]": "N[C@@H](CSCC(=O)N)C(=O)O",
    "D": "N[C@@H](CC(=O)O)C(=O)O",
    "E": "N[C@@H](CCC(=O)O)C(=O)O",
    "F": "N[C@@H](Cc1ccccc1)C(=O)O",
    "G": "NCC(=O)O",
    "H": "N[C@@H](CC1=CN=C-N1)C(=O)O",
    "I": "N[C@@H](C(CC)C)C(=O)O",
    "K": "N[C@@H](CCCCN)C(=O)O",
    "K[Acetyl]": "N[C@@H](CCCCNC(=O)C)C(=O)O",
    "K[Crotonyl]": "N[C@@H](CCCCNC(C=CC)=O)C(=O)O",
    "K[Dimethyl]": "N[C@@H](CCCCN(C)C)C(=O)O",
    "K[Formyl]": "N[C@@H](CCCCNC=O)C(=O)O",
    "K[Malonyl]": "N[C@@H](CCCCNC(=O)CC(O)=O)C(=O)O",
    "K[Methyl]": "N[C@@H](CCCCNC)C(=O)O",
    "K[Propionyl]": "N[C@@H](CCCCNC(=O)CC)C(=O)O",
    "K[Succinyl]": "N[C@@H](CCCCNC(CCC(O)=O)=O)C(=O)O",
    "K[Trimethyl]": "N[C@@H](CCCC[N+](C)(C)C)C(=O)O",
    "L": "N[C@@H](CC(C)C)C(=O)O",
    "M": "N[C@@H](CCSC)C(=O)O",
    "M[Oxidation]": "N[C@@H](CCS(=O)C)C(=O)O",
    "N": "N[C@@H](CC(=O)N)C(=O)O",
    "P": "N1[C@@H](CCC1)C(=O)O",
    "P[Oxidation]": "N1CC(O)C[C@H]1C(=O)O",
    "Q": "N[C@@H](CCC(=O)N)C(=O)O",
    "R": "N[C@@H](CCCNC(=N)N)C(=O)O",
    "R[Deamidated]": "N[C@@H](CCCNC(N)=O)C(=O)O",
    "R[Dimethyl]": "N[C@@H](CCCNC(N(C)C)=N)C(=O)O",
    "R[Methyl]": "N[C@@H](CCCNC(=N)NC)C(=O)O",
    "S": "N[C@@H](CO)C(=O)O",
    "T": "N[C@@H](C(O)C)C(=O)O",
    "V": "N[C@@H](C(C)C)C(=O)O",
    "W": "N[C@@H](CC(=CN2)C1=C2C=CC=C1)C(=O)O",
    "Y": "N[C@@H](Cc1ccc(O)cc1)C(=O)O",
    "Y[Nitro]": "N[C@@H](Cc1ccc(O)c(N(=O)=O)c1)C(=O)O",
    "Y[Phospho]": "N[C@@H](Cc1ccc(OP(O)(=O)O)cc1)C(=O)O",
    "[Acetyl]-A": "N(C(C)=O)[C@@H](C)C(=O)O",
    "[Acetyl]-C": "N(C(C)=O)[C@@H](CS)C(=O)O",
    "[Acetyl]-D": "N(C(=O)C)[C@H](C(=O)O)CC(=O)O",
    "[Acetyl]-E": "N(C(=O)C)[C@@H](CCC(O)=O)C(=O)O",
    "[Acetyl]-F": "N(C(C)=O)[C@@H](Cc1ccccc1)C(=O)O",
    "[Acetyl]-G": "N(C(=O)C)CC(=O)O",
    "[Acetyl]-H": "N(C(=O)C)[C@@H](Cc1[nH]cnc1)C(=O)O",
    "[Acetyl]-I": "N(C(=O)C)[C@@H]([C@H](CC)C)C(=O)O",
    "[Acetyl]-K": "N(C(C)=O)[C@@H](CCCCN)C(=O)O",
    "[Acetyl]-L": "N(C(=O)C)[C@@H](CC(C)C)C(=O)O",
    "[Acetyl]-M": "N(C(=O)C)[C@@H](CCSC)C(=O)O",
    "[Acetyl]-N": "N(C(C)=O)[C@@H](CC(=O)N)C(=O)O",
    "[Acetyl]-P": "N1(C(=O)C)CCC[C@H]1C(=O)O",
    "[Acetyl]-Q": "N(C(=O)C)[C@@H](CCC(=O)N)C(=O)O",
    "[Acetyl]-R": "N(C(C)=O)[C@@H](CCCN=C(N)N)C(=O)O",
    "[Acetyl]-S": "N(C(C)=O)[C@@H](CO)C(=O)O",
    "[Acetyl]-T": "N(C(=O)C)[C@@H]([C@H](O)C)C(=O)O",
    "[Acetyl]-V": "N(C(=O)C)[C@@H](C(C)C)C(=O)O",
    "[Acetyl]-W": "N(C(C)=O)[C@@H](Cc1c2ccccc2[nH]c1)C(=O)O",
    "[Acetyl]-Y": "N(C(C)=O)[C@@H](Cc1ccc(O)cc1)C(=O)O"
}

residues_reverse = {}
def register_peptide_residues(residues_: dict[str, str], canonicalize=True):
    for residue, smiles in residues_.items():
        if canonicalize:
            smiles = Chem.MolToSmiles(Chem.MolFromSmiles(smiles))
        residues[residue] = smiles
        residues_reverse[residues[residue]] = residue
    
register_peptide_residues(residues, canonicalize=False)

def _extract_residue_type(residue_tag: str) -> str:
    pattern = r"(?<!\[)[A-Z](?![^\[]*\])"
    return [match.group(0) for match in re.finditer(pattern, residue_tag)][0]

special_residues = {}
for key, value in residues.items():
    special_residues[key + '-[X]'] = value.rstrip('O')

register_peptide_residues(special_residues, canonicalize=False)
