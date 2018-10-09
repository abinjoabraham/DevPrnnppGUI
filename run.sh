 python src/InteractiveGUIforPolyrnn.py \
	--PolyRNN_metagraph='../polyrnn/models/poly/polygonplusplus.ckpt.meta' \
        --PolyRNN_checkpoint='../polyrnn/models/poly/polygonplusplus.ckpt' \
        --EvalNet_checkpoint='../polyrnn/models/evalnet/evalnet.ckpt' \
        --InputFolder='imgs/' \
        --GGNN_checkpoint='../polyrnn/models/ggnn/ggnn.ckpt' \
        --GGNN_metagraph='../polyrnn/models/ggnn/ggnn.ckpt.meta' \
        --OutputFolder='output/' \
        --Use_ggnn=True
