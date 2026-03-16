from scalpel.cfg import CFGBuilder

cfg = CFGBuilder().build_from_file("observer", "test_observer.py")

if "Store" in cfg.class_cfgs:
    class_cfg = cfg.class_cfgs["Store"]
    for (block_id, fun_name), fun_cfg in class_cfg.functioncfgs.items():
        if fun_name == "notify":
            dot = fun_cfg.build_visual('png')
            dot.render("notify_cfg", view=True)