#' prepare data and calculate fluxes in influx_si package.
#'
#' @param fkvh file name from which input data are read
#' @param e environment in which variables will be created
#' @return None All resulting content is stored in e
#options(error=function() traceback(3))
options(error = function() {
  calls <- sys.calls()
  if (length(calls) >= 2L) {
    sink(stderr())
    on.exit(sink(NULL))
    cat("Backtrace:\n")
    calls <- rev(calls[-length(calls)])
    for (i in seq_along(calls)) {
      cat(i, ": ", deparse(calls[[i]], nlines = 1L), "\n", sep = "")
    }
  }
  if (!interactive()) {
    q(status = 1)
  }
})

prep=function(fkvh, e) {
    # read basic input values
    l=kvh::kvh_read(fkvh, comment_str="#", skip_blank=TRUE, split_str="\t")
    list2env(l, envir=e)
    e$il=l
    e$labargs=e
    e$case_i=as.logical(e$case_i)
    # create log/err
    if (nchar(e$dirres)) {
        e$write_res=TRUE
        e$fcerr=file(file.path(e$dirres, sprintf("%s.err", e$baseshort)), "ab")
        e$fclog=file(file.path(e$dirres, sprintf("%s.log", e$baseshort)), "ab")
        #on.exit(close(e$fcerr), add=TRUE)
        #on.exit(close(e$fclog), add=TRUE)
    } else {
        e$write_res=FALSE
        e$fcerr=base::stderr()
        e$fclog=base::stdout()
    }
    if (options()$warn == 0L)
        options(warn=1L)
    options(digits.secs=2L)
    source(file.path(e$dirr, "libs.R"), echo=FALSE, local=e)
    # define matprod for simple_triplet_matrix
    .GlobalEnv$`%stm%` = slam::matprod_simple_triplet_matrix
    # default options
    with(e, {
        version=FALSE
        noopt=FALSE
        noscale=FALSE
        meth="nlsic"
        fullsys=FALSE
        emu=FALSE
        irand=FALSE
        sens=""
        cupx=0.999
        cupn=1.e3
        cupp=1.e5
        clownr=0.
        cinout=0.
        clowp=1.e-8
        np=0L
        ln=FALSE
        tikhreg=FALSE
        sln=FALSE
        lim=FALSE
        zc=-.Machine$double.xmax
        ffguess=FALSE
        addnoise=FALSE
        fseries=""
        iseries=""
        seed=-.Machine$integer.max
        excl_outliers=FALSE
        TIMEIT=FALSE
        prof=FALSE
        tstart=0.
        time_order="1"
        wkvh=FALSE
        tol=1.e-10
        DEBUG=FALSE
    })
    
    # evaluate r options
    if (length(e$ropts))
        for (o in strsplit(e$ropts, "\n", fixed=TRUE)[[1L]])
            eval(parse(text=o), env=e)
    with(e, {
    top_chrono("init", file=fclog)
    # update nbsys
    if (!fullsys)
       nbsys$label_variables$full=NULL
    if (emu) {
       x=s2i(nbsys$label_variables$reduced_cumomers)
       nbsys$label_variables$reduced_cumomers=NULL
       nbsys$label_variables$emu=paste(x, "*", seq_len(length(x)), "=", x*seq_len(length(x)))
        suppressWarnings(rm(x))
    }
    })
    # store nm_<smth> into nml$<smth> as 'name list'
    nme=names(e)
    nms=nme[startsWith(nme, "nm_")]
    e$nml=setNames(lapply(nms, function(nm) {it=e[[nm]]; if (identical(nchar(it), 0L)) character(0L) else it}), substring(nms, 4L))
    suppressWarnings(rm(list="nm_" %s+% names(e$nml), envir=e))
    # add nml$exp
    e$nml$exp=names(e$meas)
    e$nbl$exp=length(e$nml$exp)
    
    # store nb_<smth> into nbl$<smth> as 'number list'
    nms=nme[startsWith(nme, "nb_")]
    e$nbl=setNames(lapply(nms, function(nm) {it=e[[nm]]; if (identical(nchar(it), 0L)) character(0L) else s2i(it)}), substring(nms, 4L))
    # cumulated rcumos
    e$nbl$crcumos=c(0, cumsum(e$nbl$rcumos))
#browser()
    suppressWarnings(rm(list="nb_" %s+% names(e$nbl), envir=e))
    
    # integer values
    lapply(c("clen"), function(nm) e[[nm]]=s2i(e[[nm]]))
    # double float values
    lapply(c("ffn", "ffx", "fcn", "fcx", "fln", "flx", "fgr", "fmn", "fmndev", "poolf", "poolc", "poolm", "poolmdev"),
        function(nm) e[[nm]]=s2d(e[[nm]]))
    e$xi[]=lapply(e$xi, s2i)
    
    # composite vectors
    with(e, {
    nml$ff=c(nml$ffn, nml$ffx)
    nml$fc=c(nml$fcn, nml$fcx)
    nml$fl=c(nml$fln, nml$flx)
    nml$fallnx=c(nml$fln, nml$ffn, nml$fcn, nml$fgr, nml$flx, nml$ffx, nml$fcx, sub(".n.", ".x.", nml$fgr, fixed=TRUE))
    nml$incu=c("one", nml$xi, nml$rcumo)
    nml$ineq=c(nml$inn, nml$inx)
    # complete nbl$<smth> for numbers from nml
    nbl=c(nbl, setNames(as.list(lengths(nml)), names(nml)))
    })
    # set names to vectors of the same length that names
    lapply(names(e$nml), function(nm) if (!is.null(e[[nm]]) && (length(e[[nm]]) == e$nbl[[nm]])) e[[nm]]=setNames(e[[nm]], e$nml[[nm]]) else NULL)
    # basic setup
    with(e, {
    # synonymous
    myver=version
    optimize=!noopt
    methods=trimws(strsplit(meth, ",")[[1L]])
    sensitive=sens
    least_norm=ln
    initrand=irand

    # sanity check for command line parameters
    if (TRUE) {
        if (substring(sensitive, 1L, 3L)=="mc=") {
           # read the mc iteration number
           nmc=as.integer(substring(sensitive, 4L))
           sensitive="mc"
        } else if (sensitive=="mc") {
           nmc=10L
        } else if (nchar(sensitive) > 0L) {
           stop_mes("Option '--sens SENS' got unknown argument SENS '", sensitive,"'\n",
              "Expected 'mc[=N]' where optional N is a number of Monter-Carlo iterations", file=fcerr)
        }
        # cupx==0 means no upper limit => cupx=1
        cupx=ifelse(cupx, cupx, 1.)
        if (cupx < 0. || cupx > 1.) {
           stop_mes("Option '--cupx N' must have N in the interval [0,1L]\n",
              "Instead, the value ", cupx, " is given.", file=fcerr)
        }
        if (cinout < 0.) {
           stop_mes("Option '--cinout N' must have N non negative\n",
              "Instead, the value ", cinout, " is given.", file=fcerr)
        }
        # minimization method
        validmethods=c("BFGS", "Nelder-Mead", "SANN", "ipopt", "nlsic", "pso")
        if (! all(igood <- (methods %in% validmethods))) {
           cat(paste("***Warning: optimization methods ", paste0(methods[!igood], collapse=", "), " are not implemented. 'nlsic' is used instead."), "\n", sep="", file=fclog)
           methods[!igood]="nlsic"
        }
        if ("ipopt" %in% methods) {
           installed=suppressPackageStartupMessages(library(ipoptr, logical.return=TRUE))
           if (!installed) {
              stop_mes("An optimization method ipopt is requested but not available in this R installation", file=fcerr)
           }
        }
        if (least_norm && sln) {
           stop_mes("Options --ln and --sln cannot be activated simultaniously.", file=fcerr)
        }

        avaco=try(detectCores(), silent=TRUE)
        if (inherits(avaco, "try-error")) {
           avaco=NULL
        }
        if (np > 0L && np < 1L) {
           np=round(avaco*np)
        } else if (np >= 1L) {
           np=round(np)
        } else {
           np=avaco
        }
        if (is.null(np) || np <= 0L) {
           np=1L
        }
        if (sensitive=="mc") {
           np=min(np, nmc)
        }
        options(mc.cores=np)

        if (least_norm+tikhreg+lim > 1L) {
           stop_mes("Options --ln, --lim and --tikhreg cannot be activated simultaneously. Use only one of them at a time.", file=fcerr)
        }
        lsi_fun=lsi
        if (least_norm || sln) {
           lsi_fun=lsi_ln
        } else if (tikhreg) {
           lsi_fun=lsi_reg
        } else if (lim) {
           suppressPackageStartupMessages(library(limSolve));
           lsi_fun=lsi_lim
        }
        if (zc==-.Machine$double.xmax) {
           # no zero scrossing to apply
           zerocross=FALSE
        } else {
           if (zc < 0.) {
              stop_mes("Zero crossing value ZC must be non negative, instead ", zc, " is given.", file=fcerr)
           }
           zerocross=TRUE
        }
        if (seed==-.Machine$integer.max) {
           # no seed to apply
           set_seed=FALSE
        } else {
           set_seed=TRUE
           set.seed(seed)
        }
        if (prof) {
           Rprof(sprintf("%s.Rprof", baseshort))
        }
    }
    # get some cumomer tools
    source(file.path(dirr, "opt_cumo_tools_kvh.R"), echo=FALSE, local=e)
    if (case_i) {
        time_order=gsub("\\\\s", "", time_order) # remove spaces if any
        if (!(time_order %in% c("1", "2", "1,2"))) {
           stop_mes("time_order must be '1', '2' or '1,2'. Instead got '", time_order, "'", file=fcerr)
        }
        source(file.path(dirr, "opt_icumo_tools_kvh.R"), echo=FALSE, local=e)
        lab_resid=icumo_resid
        lab_sim=param2fl_usm_rich
        names(funlabli)=nml$exp
    }
    lab_resid=cumo_resid
    lab_sim=param2fl_x
    jx_f=new.env()
    if (emu) {
        nbl$emus=nbl$rcumos*(seq_len(nbl$rw)+1L)
        nml$x=nml$emu
        nbl$x=nbl$emu
        xiemu=lapply(xiemu, setNames, nml$xiemu)
        nml$inp=nml$xiemu
        xi=xiemu
        nml$inemu=c("one", nml$xiemu, nml$emu)
        nml$inlab=nml$inemu
    } else
        nml$x=nml$rcumo
        nbl$x=nbl$rcumos
    }) # end with()
    # prepare mat vec
    with(e, {
    top_chrono("stoichiom", file=fclog)
    # initialize the linear system Afl*flnx=bfl (0-weight cumomers)
    # prepare free fluxes and all pools
    ff=c(ffn, ffx)
    fc=c(fcn, fcx)
    ff=c(ffn, ffx)
    # set pool names as plain metabs (i.e. omit "pc:" and "pf:" prefixes)
    if (!is.null(nml$poolf))
        names(nml$poolf)=substring(nml$poolf, 4L)
    if (!is.null(nml$poolc))
        names(nml$poolc)=substring(nml$poolc, 4L)
    nml$poolall=c(nml$poolf, nml$poolc)
    poolall=setNames(c(poolf, poolc), nml$poolall)
    pool=poolall
    nbl$poolall=length(nml$poolall)
    if (case_i) {
       # check the coherence of metabolites/cumomers
       met_net=strsplitlim(nml$rcumo, ":", fixed=TRUE, lim=3L, mat=TRUE)[,1L]
       net_pool=sort(setdiff(met_net, names(nml$poolall)))
       if (length(net_pool) > 0L) {
          stop_mes("The following metabolites are internal in NETWORK section but not in METABOLITE_POOLS one:\\n", paste(net_pool, collapse="\n"), file=fcerr)
       }
       suppressWarnings(rm(met_net, net_pool))
    }

    # flux matrix
    Afl=simple_triplet_matrix(s2i(Afl$i), s2i(Afl$j), s2d(Afl$v), dimnames=list(nml$rows, nml$fl))
    # prepare pcgc2bfl matrix such that pcgc2bfl%*%c(c(ff,fc,fgr,1)) -> bfl
    nml$pcgc=c(nml$ff, nml$fc, nml$fgr, "")
    pcgc2bfl=simple_triplet_matrix(s2i(fl2bfl$i), match(fl2bfl$j, nml$pcgc), s2d(fl2bfl$v), nrow=nbl$rows, ncol=length(nml$pcgc), dimnames=list(nml$rows, nml$pcgc))
    param=ff # start building param: ff, scales, poolf

    if (ffguess) {
        top_chrono("ffguess", file=fclog)
        # make an automatic guess for free/dependent flux partition
        afd=as.matrix(cbind(Afl, -pcgc2bfl[,seq_len(nbl$ff), drop=FALSE]))
        qafd=qr(afd, LAPACK=TRUE)
        d=abs(diag(qafd$qr))
        rank=sum(d >= d[1L]*tol)
        qrow=qr(t(afd))
        rankr=qrow$rank
        if (rank != rankr)
           stop_mes("Weird error: column and row ranks of augmented Afl are not equal.", file=fcerr)
        
        irows=qrow$pivot[seq_len(rankr)]
        if (rank==0)
           stop_mes("Error: No free/dependent flux partition could be made. Stoichiometric matrix has rank=0.", file=fcerr)
        Afl=afd[irows, qafd$pivot[1L:rank], drop=FALSE]
        ka=kappa(Afl)
        if (ka > 1.e7) {
           mes=sprintf("Error: No working free/dependent flux partition could be proposed. Stoichiometric matrix has condition number %g.\\n", ka)
           stop_mes(mes, file=fcerr)
        }
        pcgc2bfl=cbind(-as.simple_triplet_matrix(afd[irows, qafd$pivot[-seq_len(rank)], drop=FALSE]), pcgc2bfl[irows,-seq_len(nbl$ff), drop=FALSE])
        
        # replace names
        nml$fl=paste("d", substring(colnames(Afl), 2L), sep="")
        colnames(Afl)=nml$fl # both net and xch
        nml$fln=sort(nml$fl[startsWith(nml$fl, "d.n")])
        nml$flx=sort(nml$fl[startsWith(nml$fl, "d.x")])
        nml$fl=c(nml$fln, nml$flx)
        Afl=Afl[, nml$fl, drop=FALSE]
        
        nbl$ff=ncol(afd)-rank
        nml$ff=paste("f", substring(nml$pcgc[seq_len(nbl$ff)], 2L), sep="")# both net and xch
        nml$pcgc[seq_len(nbl$ff)]=nml$ff
        colnames(pcgc2bfl)=nml$pcgc
        nml$ffn=sort(nml$ff[startsWith(nml$ff, "f.n")])
        nml$ffx=sort(nml$ff[startsWith(nml$ff, "f.x")])
        nml$ff=c(nml$ffn, nml$ffx)
        pcgc2bfl[,seq_len(nbl$ff)]=pcgc2bfl[, nml$ff, drop=FALSE]
        
        # redo fallnx
        nml$fallnx=c(nml$fln, nml$ffn, nml$fcn, nml$fgr, nml$flx, nml$ffx, nml$fcx, sub(".n.", ".x.", nml$fgr, fixed=TRUE))

        # redo param vector
        param=setNames(runif(nbl$ff), nml$ff)
        nml$param=nml$ff
        # redo lengths
        nms=c("ffn", "ffx", "fln", "flx", "ff", "fl", "param")
        nbl[nms]=lengths(nml[nms])
        suppressWarnings(rm(afd, qafd, rank, rankr, irows, ka))
    }
    # translation from all n-x to fw-rv
    sh_fwrv=substring(nml$fwrv[1:(nbl$fwrv/2L)], 5L)
    sh_nx=substring(nml$fallnx, 2L)
    nbl$inet2ifwrv=match(paste(".n.", sh_fwrv, sep=""), sh_nx)
    nbl$ixch2ifwrv=match(paste(".x.", sh_fwrv, sep=""), sh_nx)
    suppressWarnings(rm(sh_fwrv, sh_nx))
    
    # normalize inout and notrev flux names (add "d.n.", "f.n." etc)
    nml$inout=nml$fallnx[match(nml$inout, substring(nml$fallnx, 5L))]
    nml$notrev=nml$fallnx[match(nml$notrev, substring(nml$fallnx, 5L))]
    
    # QR Afl
    qrAfl=qr(Afl, LAPACK=TRUE)
    d=abs(diag(qrAfl$qr))
    qrAfl$rank=sum(d > d[1L]*1.e-10)
    rank=qrAfl$rank
    aful=as.matrix(cbind(Afl, -pcgc2bfl[,startsWith(nml$pcgc, c("f", "c")),drop=FALSE]))
    qrow=qr(t(aful))
    rankr=qrow$rank
    # first check the presence of lindep rows
    if (nrow(Afl) > rankr) {
       # find list of independent metabs for dependent ones
       idep=qrow$pivot[(rankr+1):nrow(Afl)]
       dcoef=qr.solve(t(aful[-idep,,drop=FALSE]), t(aful[idep,,drop=FALSE]))
       lidep=apply(dcoef, 2L, function(v) names(which(abs(v) >= 1.e-10)), simplify=FALSE)
       prop=sprintf("***Warning: Among %d equations (rows), %d are redundant.\nThe dependencies are:\n\t", nrow(Afl), nrow(Afl)-rankr)
       prop=paste0(prop, paste0(lapply(names(lidep), function(nm) paste0(nm, ": ", paste0(lidep[[nm]], collapse=", "))), collapse="\n\t"), "\nThe redundant balances for species '", paste0(names(lidep), collapse="', '"), "' will be ignored.\n")
       cat(prop, file=fclog)
       Afl=Afl[-idep,,drop=FALSE]
       rankr=nrow(Afl)
       qrAfl=qr(Afl, LAPACK=TRUE)
       d=abs(diag(qrAfl$qr))
       qrAfl$rank=sum(d > d[1L]*1.e-10)
       rank=qrAfl$rank
       pcgc2bfl=pcgc2bfl[-idep,,drop=FALSE]
    }
    pcgc2bfl=as.simple_triplet_matrix(pcgc2bfl)
    if (nrow(Afl) != rank || nrow(Afl) != ncol(Afl)) {
       mes=NULL
       if (nrow(Afl) <= rank) {
          mes=paste("Candidate(s) for free or constrained flux(es):\n",
             paste(colnames(Afl)[-qrAfl$pivot[1L:nrow(Afl)]], collapse="\n"),
             "\nFor this choice, condition number of stoichiometric matrix will be ",
             kappa(Afl[,qrAfl$pivot[1L:nrow(Afl)],drop=FALSE]), "\n", sep="")
       } else if (nrow(Afl) > rank) {
          nextra=nrow(Afl)-rank
          comb=combn(c(nml$ffn, colnames(Afl)[-qrAfl$pivot[1L:rank]]), nextra)
          aextra=cbind(Afl[,-qrAfl$pivot[1L:rank],drop=FALSE], -pcgc2bfl[, startsWith(nml$pcgc, "f"), drop=FALSE])
          ara=Afl[,qrAfl$pivot[1L:rank],drop=FALSE]
          i=which.min(apply(comb, 2L, function(i) kappa(cbind(ara, aextra[,i]))))[1L]
          nmtmp=comb[,i]
          ka=kappa(cbind(ara, aextra[,nmtmp]))
          if (ka < 1.e7) {
             prop=paste("Proposal to declare dependent flux(es) is:\n",
                paste(nmtmp, collapse="\n"), "\n", sep="")
             if (rank < ncol(Afl)) {
                prop=prop%s+%"While the following dependent flux(es) should be declared free or constrained:\n"%s+%join("\n", colnames(Afl)[-qrAfl$pivot[1L:rank]])%s+%"\n"
             }
             prop=paste(prop, "For this choice, condition number of stoichiometric matrix will be ", ka, "\n", sep="")
          } else {
             aextended=aful
             qae=qr(aextended, LAPACK=TRUE)
             d=abs(diag(qae$qr))
             ranke=sum(d > d[1L]*1.e-10)
             if (ranke == nrow(Afl)) {
                prop=paste("Proposal to declare dependent flux(es) is:\n",
                join("\n", colnames(aextended)[qae$pivot[1L:ranke]]), "\n",
                "while free and constrained fluxes should be:\n",
                join("\n", colnames(aextended)[-qae$pivot[1L:ranke]]), "\n",
                sep="")
                ka=kappa(aextended[,qae$pivot[1L:ranke]])
                prop=paste(prop, "For this choice, condition number of stoichiometric matrix will be ", ka, "\n", sep="")
             } else {
                prop="No proposal for partition dependent/free fluxes could be made.\n"
             }
          }
          mes=paste("There is (are) probably ", nextra,
             " extra free flux(es) among the following:\n",
             paste(nml$ffn, collapse="\n"), "\n",
             prop,
             sep="")
       }
       stop_mes("Flux matrix is not square or is singular: (", nrow(Afl), "eq x ",
          ncol(Afl), "unk)\n", "You have to change your choice of free fluxes in the '", baseshort, "' file.\n", mes, file=fcerr)
    }

    # make sure that free params choice leads to not singular matrix
    if (qrAfl$rank != nbl$fl) {
       # make a suggestion of new free fluxes
       ifc=which(startsWithv(nml$pcgc, c("f", "c")))
       A=cbind(Afl, -pcgc2bfl[,ifc, drop=FALSE])
       qa=qr(A, LAPACK=TRUE)
       d=diag(qa$qr)
       qa$rank=sum(abs(d)>=abs(d[1L]*1.e-10))
       
       mes=paste("Error: Dependent flux matrix is singular.\n",
          "Change your partition on free/dependent/constrained fluxes in the '%(n_ftbl)s' file.\n",
          "Can not resolve dependent fluxe(s):\n",
          paste(colnames(Afl)[-qrAfl$pivot[(1:qrAfl$rank)]], collapse="\n"),
          sep="")
       if (qa$rank==nbl$fl) {
          mes=paste(mes,
          "\n\nSuggested dependent fluxes:\n",
          paste(colnames(A)[qa$pivot[(1:qa$rank)]], collapse="\n"),
          "\n\nWhich would give the following free and constrained fluxes:\n",
          paste(colnames(A)[-qa$pivot[(1:qa$rank)]], collapse="\n"), "\n",
          sep="")
       } else {
          mes=paste(mes, "\nNo suggested free fluxes could be found", sep="")
       }
       stop_mes(mes, file=fcerr)
    }

    # inverse flux matrix
    invAfl=solve(qrAfl)
    invAfl[abs(invAfl) <= tol]=0.
    # intermediate jacobians
    top_chrono("dfl_dffg", file=fclog)
    nbl$dfl_dffg=invAfl %stm% pcgc2bfl[,startsWithv(nml$pcgc, c("f", "g"))]
    nbl$dfl_dffg[abs(nbl$dfl_dffg) < 1.e-14]=0.

    # prepare ifdcg2all
    # such that  c(ff, fc, fg, fl, 0)[ifcgd2all] -> fallnx
    ifcgd2all=match(nml$fallnx, c(nml$ff, nml$fc, nml$fgr, nml$fl))
    ifcgd2all[is.na(ifcgd2all)]=nbl$ff + nbl$fc + nbl$fg + nbl$fl + 1L
    # prepare spAbr
    top_chrono("cumosys", file=fclog)
    }) # end with()

    e$spa=prep_spAbr(e$spAbr, e$emu, e)

    if (e$fullsys)
        e$spaf=prep_spAbr(e$spAbr_f, emu=FALSE, e)
    # measurements
    with(e, {
    top_chrono("measurem", file=fclog)
    jx_f=new.env()
    
    sc=nbl$sc=nml$meas=nml$measmat=nbl$measmat=nbl$meas=vector("list", nbl$exp)
    measmat=memaone=measvec=measdev=vector("list", nbl$exp)
    pwe=ipwe=ip2ipwe=ipf2ipwe=pool_factor=dpw_dpf=ijpwef=vector("list", nbl$exp)
    if (case_i) {
        measvecti=ti=tifull=tifull2=vector("list", nbl$exp)
        nbl$ti=nbl$tifu=nbl$tifu2=integer(nbl$exp)
        nsubdiv_dt=pmax(1L, s2i(nsubdiv_dt))
        nbl$ipf2ircumo=nbl$ipf2ircumo2=list()
    }
    nmpf=if (!is.null(nml$poolf)) names(nml$poolf)
    for (iexp in seq_along(meas)) {
        m=meas[[iexp]]
        # labeled measurements
        nml$meas[[iexp]]=m$nmmeas
        nml$measmat[[iexp]]=m$nmmeas_np
        nbl$meas[[iexp]]=length(m$nmmeas)
        if (nbl$meas[[iexp]] == 0L)
            stop_mes("At least one label measurement is required in '", nml$exp[[iexp]], "'")
        nbl$measmat[[iexp]]=length(m$nmmeas_np)
        measmat[[iexp]]=simple_triplet_matrix(s2i(m$mmat$i)+1L, s2i(m$mmat$j)+1L, s2d(m$mmat$v), nrow=nbl$measmat[[iexp]], ncol=length(nml$x), dimnames=list(m$nmmeas_np, nml$x))
        memaone[[iexp]]=s2d(m$memaone)
        measdev[[iexp]]=s2d(m$measdev)
        measvec[[iexp]]=s2d(m$measvec, na.rm=FALSE)
        if (!noscale) {
            # scaling factors
            sc[[iexp]]=Filter(length, n_lapply(m$sc_name, function(nm, v) {
                iv=match(v, m$nmmeas) # todo: remove extra scales for case_i
                if (anyNA(iv))
                    stop_mes("Incoherent measurement names in scales '", nm, "' and nmmeas in input kvh.", file=fcerr)
                ivv=iv[!is.na(measvec[[iexp]][iv])]
                if (length(ivv) < 2L)
                    stop_mes("Not enough valid (non NA) measurements for scale'", nm, "'", file=fcerr)
                # remove scaling when MS with complete fragment summing to 1.
                if (all(startsWith(m$nmmeas[ivv], "m"))) {
                    met=strsplitlim(m$nmmeas[ivv], ":", fixed=TRUE, lim=4L, mat=TRUE)
                    lenfrag=ncol(strsplitlim(met[,3L], ",", fixed=TRUE, lim=NA, mat=TRUE))
                    met=trimws(strsplitlim(met[,2L], "+", fixed=TRUE, lim=NA, mat=TRUE)[,1L])
                    if (lenfrag == 0L)
                        lenfrag=clen[met[1L]]
                    s <- sum(measvec[[iexp]][ivv])
                    if (lenfrag+1L == length(ivv) && abs(s - 1.) <= tol) {
                        NULL
                    } else {
                        bop(measvec[[iexp]], as.matrix(ivv), "*=", 1./s) # mv /= sum
                        ivv # todo: update sd
                    }
                } else {
                    ivv
                }
            }))
            nbl$sc[[iexp]]=length(sc[[iexp]])
        }
        # pooled measurements
        # they are calculated as: mv=meas2sum[[iexp]] %stm% (pwe[[iexp]]*mx)
        # where pwe is pwe[[iexp]][ipwe[[iexp]]]=pool[ip2ipwe[[iexp]]]
        # spwe=tapply(pwe[[iexp]], pool_factor[[iexp]], sum) # sum of pooled concentrations
        # spwe=1./spwe[nml$measmat[[iexp]]]
        # pwe[[iexp]]=c(pwe[[iexp]]*spwe)
        m$ipooled=Filter(length, lapply(m$ipooled, function(v) s2i(v)+1L))
        
        if (length(m$ipooled)) {
            ipwe[[iexp]]=unlist(m$ipooled) # where in meas, the weight is
            pool_factor[[iexp]]=as.factor(m$nmmeas_np)
            pwe[[iexp]]=rep(1., nbl$measmat)
            mets_in_res=strsplitlim(names(m$ipooled), ":", fixed=TRUE, lim=3L, mat=TRUE)[, 2L]
            names(mets_in_res)=names(m$ipooled)
            metsp=lapply(strsplit(mets_in_res, "+", fixed=TRUE), trimws)
            ip2ipwe[[iexp]]=lapply(metsp, function(v) which(names(nml$poolall) %in% v))
            # first 2 col for d(mx)/d(pf), the 3d for j in dpw_dpf
            ipf2ipwe[[iexp]]=Filter(length, n_lapply(ip2ipwe[[iexp]], function(nm, iv) {ii=which(iv <= nbl$poolf); if (length(ii)) cbind(imnp=m$ipooled[[nm]][ii], im=match(nm, nml$meas[[iexp]]), ipf=iv[ii]) else NULL}))
            ipf2ipwe[iexp]=list(Reduce(rbind, ipf2ipwe[[iexp]]))
            # dpw_dpf - matrix for derivation of pool weights by free pools
            if (nbl$poolf > 0L && length(ipf2ipwe[[iexp]]) > 0L) {
                dpw_dpf[[iexp]]=simple_triplet_zero_matrix(nbl$meas[[iexp]], nbl$poolf)
                dpw_dpf[[iexp]][ipf2ipwe[[iexp]][,c("im", "ipf"),drop=FALSE]]=1.
            }
            ip2ipwe[[iexp]]=unlist(ip2ipwe[[iexp]])
            ijpwef[iexp]=list(Reduce(rbind, i_lapply(metsp, function(i, mets) {
                ip=na.omit(pmatch(mets, names(nml$poolf)))
                cbind(rep(m$ipooled[i], length(ip)), rep(ip, each=length(m$ipooled[i]))) # where free pools matter
            })))
        }
        # variables for isotopomer kinetics
        if (case_i) {
            # read measvecti from file(s) specified in ftbl(s)
            nmim=nml$poolall[strsplitlim(nml$rcumo, ":", fixed=TRUE, lim=3L, mat=TRUE)[,1L]]
            if (fullsys)
                nmimf=nml$poolall[strsplitlim(nml$cumo, ":", fixed=TRUE, lim=3L, mat=TRUE)[,1L]]
            if (tmax[iexp] < 0)
                stop_mes(sprintf("The parameter tmax must not be negative (tmax=%g in '%s.ftbl')", tmax[iexp], nml$exp[iexp]), file=fcerr)
            if (dt[iexp] <= 0)
                stop_mes(sprintf("The parameter dt must be positive (dt=%g in '%s.ftbl')", dt[iexp], nml$exp[iexp]), file=fcerr)
            if (nchar(flabcin[iexp])) {
                if (substr(flabcin[iexp], 1L, 1L) == "/") {
                    flabcin[iexp]=file.path(flabcin[iexp])
                } else
                    flabcin[iexp]=file.path(dirw, flabcin[iexp])
                measvecti[[iexp]]=try(as.matrix(read.table(flabcin[iexp], header=TRUE, row.names=1, sep="\t", check=FALSE, comment="#", strip.white=TRUE)), silent=TRUE)
                if (inherits(measvecti[[iexp]], "try-error")) {
                    # try with comment '//'
                    tmp=try(kvh::kvh_read(flabcin[iexp], comment_str = "//", strip_white = FALSE, skip_blank = TRUE, split_str = "\t", follow_url = FALSE), silent=TRUE)
                    if (inherits(tmp, "try-error"))
                        stop_mes("Error while reading '", flabcin[iexp], "' from '", nml$exp[iexp], "':\n", tmp, file=fcerr)
                    nbcol=lengths(tmp)
                    if (any(ibad <- nbcol != nbcol[1L]))
                        stop_mes("Column number varies in '", flabcin[iexp], "'. First row has ", nbcol[1L], " columns while the following rows differ:\n\t", paste(c("row", which(ibad)), c("col_nb", nbcol[ibad]), sep="\t", collapse="\n\t"))

                    tmp=do.call(rbind, tmp)
                    tmp=structure(tmp[-1L,, drop=FALSE], dimnames=list(rownames(tmp)[-1L], tmp[1L,]))
                    suppressWarnings(storage.mode(tmp) <- "double")
                    measvecti[[iexp]]=tmp
                }
                nmrow=rownames(measvecti[[iexp]])
                # put in the same row order as simulated measurements
                # check if nmmeas are all in rownames
                if (all(m$nmmeas %in% nmrow)) {
                    measvecti[[iexp]]=measvecti[[iexp]][m$nmmeas,,drop=FALSE]
                } else {
                    # try to strip row number from measure id
                    nmstrip=sapply(strsplit(m$nmmeas, ":", fixed=TRUE), function(v)
                        paste(c(v[-length(v)], ""), sep="", collapse=":")
                    )
                    im=pmatch(nmstrip, nmrow)
                    if (any(ina <- is.na(im))) {
                        mes=paste("Cannot match the following measurement(s) in the file '", flabcin[iexp], "':\n", paste(m$nmmeas[ina], sep="", collapse="\n"), "\n", sep="", collapse="")
                        stop_mes(mes, file=fcerr)
                    }
                    measvecti[[iexp]]=measvecti[[iexp]][im,,drop=FALSE]
                    if (typeof(measvecti[[iexp]]) != "double") {
                        # check for weird  entries
                        tmp=measvecti[[iexp]]
                        suppressWarnings(storage.mode(tmp) <- "double")
                        if (any(ibad <- is.na(tmp) & !is.na(measvecti[[iexp]]))) {
                            ibad=which(ibad)[1L]
                            stop_mes("This entry '", measvecti[[iexp]][ibad], "' could not be converted to real number (", flabcin[iexp], ")", file=fcerr)
                        } else if (!noopt)
                            stop_mes("Entries in file '", flabcin[iexp], "' could not be converted to real numbers", file=fcerr)
                    }
                    if (!noopt && all(is.na(measvecti[[iexp]])))
                        stop_mes("All entries in file '", flabcin[iexp], "' are NA (non available).", file=fcerr)
                }
                ti[[iexp]]=as.double(colnames(measvecti[[iexp]]))
                if (any(is.na(ti[[iexp]]))) {
                    mes=sprintf("Some time moments (in column names) could not be converted to real numbers in the file '%s'\nConverted times:\n%s", flabcin[[iexp]], join("\n", ti[[iexp]]))
                    stop_mes(mes, file=fcerr)
                }
                if (length(ti[[iexp]]) < 1L) {
                    mes=sprintf("No column found in the file '%s'", flabcin[[iexp]])
                    stop_mes(mes, file=fcerr)
                }
                if (!all(diff(ti[[iexp]]) > 0.)) {
                    mes=sprintf("Time moments (in column names) are not monotonously increasing in the file '%s'", flabcin[[iexp]])
                    stop_mes(mes, file=fcerr)
                }
                if (ti[[iexp]][1L] <= 0.) {
                    mes=sprintf("The first time moment cannot be negative or 0 in the file '%s'", flabcin[[iexp]])
                    stop_mes(mes, file=fcerr)
                }
                if (ti[[iexp]][1L] != 0.)
                    ti[[iexp]]=c(tstart, ti[[iexp]])
                i=which(ti[[iexp]]<=tmax[[iexp]])
                ti[[iexp]]=ti[[iexp]][i]
                if (tmax[[iexp]] == Inf)
                    tmax[[iexp]]=max(ti[[iexp]])
                measvecti[[iexp]]=measvecti[[iexp]][,i[-1L]-1L,drop=FALSE]
            } else {
                if (tmax[[iexp]] == Inf)
                    stop_mes(sprintf("Maximal value for time is Inf (probably 'tmax' field is not set in OPTIONS section: '%%s.ftbl')", nml$exp[[iexp]]), file=fcerr)
                ti[[iexp]]=seq(tstart, tmax[[iexp]], by=dt[iexp])
                if (optimize) {
                    cat(sprintf("***Warning: a fitting is requested but no file with label data is provided by 'file_labcin' option in '%%s.ftbl' file.
	The fitting is ignored as if '--noopt' option were set.\\n", nml$exp[[iexp]]), file=fclog)
                    optimize=FALSE
                }
            }
            if (length(ti[[iexp]]) < 2L) {
               mes=sprintf("After filtering by tmax, only %d time moments are kept for experiment '%s'. It is not sufficient.", length(ti[[iexp]], nml$exp[[iexp]]))
               stop_mes(mes, file=fcerr)
            }
            nbl$ti[[iexp]]=length(ti[[iexp]])
            # recalculate nbl$meas from measvecti
            nbl$meas[[iexp]]=NROW(measvecti[[iexp]])
            # divide each time interval by nsubdiv_dt
            tifull[[iexp]]=ti[[iexp]]
            dt=diff(tifull[[iexp]])
            dt=rep(dt/nsubdiv_dt[iexp], each=nsubdiv_dt[iexp])
            tifull[[iexp]]=c(tifull[[iexp]][1L], cumsum(dt))
            nbl$tifu[iexp]=length(tifull[[iexp]])
            
            tifull2[[iexp]]=c(tifull[[iexp]][1L], tifull[[iexp]][1L]+cumsum(rep(diff(tifull[[iexp]])/2., each=2L)))
            nbl$tifu2[iexp]=length(tifull2[[iexp]])
            
            if (length(ijpwef[[iexp]])) {
                # vector index for many time points
                ijpwef[[iexp]]=cbind(ijpwef[[iexp]][,1L], rep(seq_len(nbl$ti[[iexp]]-1L), each=nrow(ijpwef[[iexp]])), ijpwef[[iexp]][,2L])
                dp_ones[[iexp]]=matrix(aperm(array(dp_ones[[iexp]], c(dim(dp_ones[[iexp]]), nbl$ti[[iexp]]-1L)), c(1L, 3L, 2L)), ncol=nbl$poolf)
            }
        }
    }
    suppressWarnings(rm(mets_in_res, metsp, nmpf, dt))
    nbl$sc_tot=sum(unlist(nbl$sc))
    # pool measurements, poolm is ready from kvh
    # inverse of variance for pool measurements
    names(poolmdev)=nml$poolm
    # simulated metabolite measurements are calculated as
    # measmatpool %stm% poolall -> poolm
    i=s2i(mmatp$i)
    measmatpool=simple_triplet_matrix(i=i, j=s2i(mmatp$j), v=rep(1., length(i)), nrow=nbl$poolm, ncol=nbl$poolall, dimnames=list(nml$poolm, nml$poolall))
    # flux measurements
    fmndev=setNames(fmndev, nml$fmn)
    ifmn=match(paste(".n.", nml$fmn, collapse="", sep=""), substring(nml$fallnx, 2L))
    # gather all measurement information
    measurements=list(
        vec=list(labeled=measvec, flux=fmn, pool=poolm, kin=if (case_i) measvecti else NULL),
        dev=list(labeled=measdev, flux=fmndev, pool=poolmdev, kin=if (case_i) i_lapply(measdev, function(i, v) {nbc=if (is.null(measvecti[[i]])) 0 else ncol(measvecti[[i]]); suppressWarnings(matrix(v, nrow=length(v), ncol=nbc))}) else NULL),
        mat=list(labeled=measmat, flux=ifmn, pool=measmatpool),
        one=list(labeled=memaone)
    )
    measurements$dev$all_inv=with(measurements$dev, 1./c(unlist(if (case_i) kin else labeled), flux, pool))
    nml$resid=c(if (case_i) unlist(i_lapply(measvecti, function(iexp, mti) {m=outer(rownames(mti), colnames(mti), paste, sep=", t="); if (length(m) > 0L) paste(iexp, m, sep=":", recycle0=TRUE) else character(0L)})) else unlist(i_lapply(nml$meas, function(iexp, v) paste(iexp, v, sep=":"))), nml$fmn, nml$poolm)
    nbl$resid=length(nml$resid)
    
    # finalize param (after defining scale factors in measurements)
    param=c(param, poolf)
    nml$param=names(param)
    nbl$param=length(param)
    }) # end with()
    
    # inequalities
    with(e, {
    top_chrono("inequal", file=fclog)

    # prepare mi matrix and li vector
    # such that mi*fallnx>=li corresponds
    # to the inequalities given in ftbl file
    li=s2d(mi$li)
    mi=simple_triplet_matrix(s2i(mi$i), na.omit(match(mi$j, substring(nml$fallnx, 3L))), s2d(mi$v), nrow=length(li), ncol=nbl$fallnx, dimnames=list(nml$ineq, nml$fallnx))
    # explicit inequalities take precedence over generic ones
    # so eliminate fluxes which are already in inequalities
    
    # whether flux is present alone in flux >= smth
    j1p=nml$fallnx[as.integer(names(table(mi$j[mi$v == 1.])))]
    # whether flux is present alone in flux <= smth
    j1n=nml$fallnx[as.integer(names(table(mi$j[mi$v == -1.])))]
    # add standard limits
    nmup=c(flx=cupx, ffx=cupx, fln=if(cupn == 0.) Inf else cupn)
    nmlow=c(flx=0., ffx=0., fln=if(cupn == 0.) -Inf else -cupn, inout=cinout, notrev=if (clownr == 0.) -Inf else clownr)
    for (nm in unique(c(names(nmlow), names(nmup)))) {
        # >= low
        # exclude those already in mi
        nmkeep=nml[[nm]][! nml[[nm]] %in% j1p]
        nbkeep=length(nmkeep)
        if (!is.na(nmlow[nm]) && nmlow[nm] != -Inf && nbkeep > 0L) {
            tmp=simple_triplet_matrix(i=seq(nbkeep), j=match(nmkeep, nml$fallnx), v=rep(1., nbkeep), ncol=nbl$fallnx, dimnames=list(paste("low ", nm, ":", nmkeep, ">=", nmlow[nm], sep=""), NULL))
            mi=rbind(mi, tmp)
            li=c(li, rep(nmlow[nm], nbkeep))
        }
        # <= up
        # exclude those already in mi
        nmkeep=nml[[nm]][! nml[[nm]] %in% j1n]
        nbkeep=length(nmkeep)
        if (!is.na(nmup[nm]) && nmup[nm] != Inf && nbkeep > 0L) {
            tmp=simple_triplet_matrix(i=seq(nbkeep), j=match(nmkeep, nml$fallnx), v=rep(-1., nbkeep), ncol=nbl$fallnx, dimnames=list(paste("up ", nm, ":", nmkeep, "<=", nmup[nm], sep=""), NULL))
            mi=rbind(mi, tmp)
            li=c(li, rep(-nmup[nm], nbkeep))
        }
    }
    names(li)=rownames(mi)
    # remove inequalities with only constrained fluxes
    jc=which(startsWith(nml$fallnx, "c"))
    ic=Filter(I, sapply(unique(mi$i), function(ii) if (all(mi$j[mi$i==ii] %in% jc)) ii else 0L))
    if (length(ic)) {
        mi=mi[-ic,,drop=FALSE]
        li=li[-ic]
    }
    # replace d. fluxes by (ff,fc) linear combinations
#browser()
    jd=nml$fallnx[startsWithv(nml$fallnx, "d")]
    jfc=nml$fallnx[startsWithv(nml$fallnx, c("f", "c"))]
    jc=nml$fallnx[startsWithv(nml$fallnx, "c")]
    li=li - mi[,jc,drop=FALSE] %stm% fc[jc] - (mi[,jd,drop=FALSE] %stm% (invAfl %stm% pcgc2bfl[,nml$pcgc=="",drop=FALSE])[jd,,drop=FALSE])
    mi=mi[,jfc,drop=FALSE] + as.simple_triplet_matrix(mi[,jd,drop=FALSE] %stm% (invAfl %stm% pcgc2bfl[,startsWithv(nml$pcgc, c("f", "c")),drop=FALSE])[jd,,drop=FALSE])[,jfc,drop=FALSE]
    # move fc part to li so that only ff remains
    jc=colnames(mi)[startsWith(colnames(mi), "c")]
    mi=mi[,startsWith(colnames(mi), "f"),drop=FALSE]
    # spot fluxes that are in inequalities in alone mode (for --zc)
    ige=rownames(mi)[apply(mi, 1L, function(v) sum(v) == 1. && sum(v != 0.) == 1L) & li >= 0.]
    ige=nml$dfn[unique(c(
        sub("n:.+<=(.+)$", "\\1", grep("^n:.+<=.+$", ige, v=TRUE)),
        sub("[df]\\.n\\.(.+)>=.+$", "\\1", grep("^[df]\\.n\\..+>=.+$", ige, v=TRUE)),
        sub("inout: [df]\\.n\\.(.+)>=.+$", "\\1", grep("^inout [df]\\.n\\..+>=.+$", ige, v=TRUE))
    ))]
    ile=rownames(mi)[apply(mi, 1L, function(v) sum(v) == 1. && sum(v != 0.) == 1L) & li >= 0.]
    ile=nml$dfn[unique(c(
        sub("n:.+<=(.+)$", "\\1", grep("^n:.+<=.+$", ile, v=TRUE)),
        sub("[df]\\.n\\.(.+)>=.+$", "\\1", grep("^[df]\\.n\\..+>=.+$", ile, v=TRUE)),
        sub("inout: [df]\\.n\\.(.+)>=.+$", "\\1", grep("^inout [df]\\.n\\..+>=.+$", ile, v=TRUE))
    ))]
    
    # metab inequalities
    if (nbl$poolf) {
        lip=s2d(mip$lip)
        i=s2i(mip$i)
        mip=simple_triplet_matrix(i=i, j=na.omit(match(mip$j, names(nml$poolall))), v=s2d(mip$v), nrow=length(lip), ncol=nbl$poolall, dimnames=list(names(lip), nml$poolall))
        # extend inequalities ui, ci by cupp>= poolf >= clowp
        # but exclude metabolites that are individually set in the mip (FTBL)
        # whether pool is present alone in pool >= smth
        j1p=as.integer(names(table(mip$j[mip$v == 1.])))
        # whether pool is present alone in pool <= smth
        j1n=as.integer(names(table(mip$j[mip$v == -1.])))
        # add standard limits
        nmup=c(flx=cupx, ffx=cupx, fln=if(cupn == 0.) Inf else cupn)
        nmlow=c(flx=0., ffx=0., fln=if(cupn == 0.) -Inf else -cupn, inout=cinout, notrev=if (clownr == 0.) -Inf else clownr)
        # >= clowp
        # exclude those already in mip
        nmkeep=if (length(j1p)) nml$poolall[-j1p] else nml$poolall
        nbkeep=length(nmkeep)
        if (nbkeep > 0L) {
            tmp=simple_triplet_matrix(i=seq(nbkeep), j=match(nmkeep, nml$poolall), v=rep(1., nbkeep), ncol=nbl$poolall, dimnames=list(paste("low:", nmkeep, ">=", clowp, sep=""), NULL))
            mip=rbind(mip, tmp)
            lip=c(lip, rep(clowp, nbkeep))
        }
        # <= cupp
        # exclude those already in mip
        nmkeep=if (length(j1n)) nml$poolall[-j1n] else nml$poolall
        nbkeep=length(nmkeep)
        if (nbkeep > 0L) {
            tmp=simple_triplet_matrix(i=seq(nbkeep), j=match(nmkeep, nml$poolall), v=rep(-1., nbkeep), ncol=nbl$poolall, dimnames=list(paste("up:", nmkeep, "<=", cupp, sep=""), NULL))
            mip=rbind(mip, tmp)
            lip=c(lip, rep(-cupp, nbkeep))
        }
        # move constant pools to rhs
        jc=nml$poolc
        lip=lip-mip[,jc] %stm% poolc
        mip=mip[,nml$poolf]
    } else {
        mip=simple_triplet_zero_matrix(0L, 0L)
        lip=c()
    }

    # prepare ui matrix and ci vector for optimisation
    # ui%*%param-ci>=0
    ui=as.matrix(dbind(mi, mip))
    ci=c(li, lip)
    names(ci)=rownames(ui)
    # remove all 0 rows (ineq on constrained values)
    inz=which(apply(ui, 1L, function(v) any(v != 0.)))
    if (length(inz)) {
        if (any(ipos <- ci[-inz] > 0.)) {
            ipos=which(ipos)
            stop_mes("Following inequalities were set on constrained values and are violated:\n\t", paste(names(ci[-inz])[ipos], sep="", collapse="\n\t"), file=fcerr)
        }
        ui=ui[inz,,drop=FALSE]
        ci=ci[inz]
    } else {
        ui=NULL
        ci=NULL
    }
    # equalities on metabs
    if (nbl$poolf) {
        cp=setNames(s2d(ep$lp), names(ep$lp))
        ep=as.matrix(simple_triplet_matrix(i=s2i(ep$i), j=match(ep$j, names(nml$poolall)), v=s2d(ep$v), ncol=nbl$poolall, dimnames=list(NULL, nml$poolall)))
        rownames(ep)=names(cp)
    } else {
        ep=cp=NULL
    }
    }) # end with()
    # prepare inputs for case_i
    with(e, {
    if (case_i) {
        for (iexp in seq_len(nbl$exp)) {
            nm=nml$exp[[iexp]]
            # funlab list
            funlabli[[iexp]]=eval(parse(text=funlabli[[iexp]]))
            funlabli[[iexp]]={
                n_lapply(funlabli[[iexp]], function(met, it) {
                    n_lapply(it, function(ni, rcode) {
                        v=try(parse(text=rcode), silent=TRUE)
                        if (inherits(v, "try-error"))
                            stop_mes("Error in parsing R code '", rcode, "' for label '", met, "#", ni, "' in '", nm, "':\n", v, file=fcerr)
                        v
                    })
                })
            }
            if (inherits(funlabli[[iexp]], "try-error"))
                stop_mes(funlabli[[iexp]], file=fcerr)
            funlabR=ifelse(nchar(funlabR), paste(dirw, funlabR, sep="/"), "") # set to "" where file names are empty
        }
        # prepare mapping of metab pools on cumomers
        nbl$ipf2ircumo[[iexp]]=nbl$ipf2ircumo2[[iexp]]=list()
        for (iw in seq_len(nbl$rw)) {
            ix=seq_len(nbl$rcumos[iw])
            ipf2ircumo=ipf2ircumo2=match(nmim[nbl$crcumos[iw]+ix], nml$poolf, nomatch=0L)
            dims=c(1L, nbl$rcumos[iw], ifelse(emu, iw, 1L), nbl$tifu[iexp]-1L)
            dims2=c(1L, nbl$rcumos[iw], ifelse(emu, iw, 1L), nbl$tifu2[iexp]-1L)
            i=as.matrix(ipf2ircumo)
            i2=as.matrix(ipf2ircumo2)
            for (id in 2L:length(dims)) {
                cstr=sprintf("cbind(%srep(seq_len(dims[id]), each=prod(dims[seq_len(id-1L)])))", paste("i[, ", seq_len(id-1L), "], ", sep="", collapse=""))
                i=eval(parse(text=cstr))
            }
            for (id in 2L:length(dims2)) {
                cstr=sprintf("cbind(%srep(seq_len(dims2[id]), each=prod(dims2[seq_len(id-1L)])))", paste("i2[, ", seq_len(id-1L), "], ", sep="", collapse=""))
                i2=eval(parse(text=cstr))
            }
            colnames(i)=c("ipoolf", "ic", "iw", "iti")
            colnames(i2)=c("ipoolf", "ic", "iw", "iti")
            i=i[i[,1L]!=0L,,drop=FALSE]
            i2=i2[i2[,1L]!=0L,,drop=FALSE]
            # put the poolf column last
            nbl$ipf2ircumo[[iexp]][[iw]]=i[, c("ic", "iw", "ipoolf", "iti"), drop=FALSE]
            nbl$ipf2ircumo2[[iexp]][[iw]]=i2[, c("ic", "iw", "ipoolf", "iti"), drop=FALSE]
        }
        if (fullsys) {
            # prepare mapping of metab pools on cumomers for full system (emu is FALSE here)
            nbl$ipf2icumo[[iexp]]=nbl$ipf2icumo2[[iexp]]=list()
            for (iw in seq_len(nbl$wf)) {
                ix=seq_len(nbl$cumos[iw])
                ipf2icumo=ipf2icumo2=match(nmimf[nbc_cumos[iw]+ix], nml$poolf, nomatch=0L)
                dims=c(1L, nbl$cumos[iw], 1L, nbl$tifu[iexp]-1L)
                dims2=c(1L, nbl$cumos[iw], 1L, nbl$tifu2[iexp]-1L)
                i=as.matrix(ipf2icumo)
                i2=as.matrix(ipf2icumo2)
                for (id in 2L:length(dims)) {
                    cstr=sprintf("cbind(%srep(seq_len(dims[id]), each=prod(dims[seq_len(id-1L)])))", paste("i[, ", seq_len(id-1L), "], ", sep="", collapse=""))
                    i=eval(parse(text=cstr))
                }
                for (id in 2L:length(dims2)) {
                    cstr=sprintf("cbind(%srep(seq_len(dims2[id]), each=prod(dims2[seq_len(id-1L)])))", paste("i2[, ", seq_len(id-1L), "], ", sep="", collapse=""))
                    i2=eval(parse(text=cstr))
                }
                colnames(i)=c("ipoolf", "ic", "iw", "iti")
                colnames(i2)=c("ipoolf", "ic", "iw", "iti")
                i=i[i[,1L]!=0L,,drop=FALSE]
                i2=i2[i2[,1L]!=0L,,drop=FALSE]
                # put the poolf column last
                nbl$ipf2icumo[[iexp]][[iw]]=i[, c("ic", "iw", "ipoolf", "iti"), drop=FALSE]
                nbl$ipf2icumo2[[iexp]][[iw]]=i2[, c("ic", "iw", "ipoolf", "iti"), drop=FALSE]
            }
        }
        xil=xi2=vector("list", nbl$exp)
        for (iexp in seq(nbl$exp)) {
            fli=funlabli[[iexp]]
            if (length(fli) == 0) {
                # replicate first column in xi as many times as there are time points
                if (time_order == "2" || time_order == "1,2")
                    xi2[[iexp]]=matrix(xi[[iexp]], nrow=length(xi[[iexp]]), ncol=nbl$tifu2[[iexp]])
                xil[[iexp]]=matrix(xi[[iexp]], nrow=length(xi[[iexp]]), ncol=nbl$tifu[[iexp]])
            }  else {
                # use funlab
                envfunlab=new.env() # funlab code won't see influx's variables
                if (nchar(funlabR[[iexp]])) {
                    if (file.exists(funlabR[[iexp]])) {
                        es=try(source(funlabR[[iexp]], local=envfunlab), outFile=fcerr)
                    } else {
                        stop_mes("funlab script R '", funlabR[[iexp]], "' from '", nml$exp[[iexp]],"' does not exist.", file=fcerr)
                    }
                }
                xil[[iexp]]=funlab(tifull[[iexp]], nml$inp, fli, envfunlab, emu, nml$exp[[iexp]], fcerr)
                if (time_order == "2" || time_order == "1,2")
                    xi2[[iexp]]=funlab(tifull2[[iexp]], nml$inp, fli, envfunlab, emu, nml$exp[[iexp]], fcerr)
            }
        }
        xi=xil
        nbl$ip2ircumo=match(nmim, nml$poolall)
        if (fullsys) {
            nbl$ip2icumo=match(nmimf, nml$poolall)
            # prepare xif from funlab
            xilf=xi2f=vector("list", nbl$exp)
            for (iexp in seq(nbl$exp)) {
                fli=funlabli[[iexp]]
                if (length(fli) == 0) {
                    # replicate first column in xi as many times as there are time points
                    if (time_order == "2" || time_order == "1,2")
                        xi2f[[iexp]]=matrix(xif[[iexp]], nrow=length(xif[[iexp]]), ncol=nbl$tifu2[[iexp]])
                    xilf[[iexp]]=matrix(xif[[iexp]], nrow=length(xif[[iexp]]), ncol=nbl$tifu[[iexp]])
                } else {
                    # use funlab
                    xilf[[iexp]]=funlab(tifull[[iexp]], nml$xif, fli, envfunlab, emu=FALSE, nml$exp[[iexp]], fcerr)
                    if (time_order == "2" || time_order == "1,2")
                        xi2f[[iexp]]=funlab(tifull2[[iexp]], nml$xif, fli, envfunlab, emu=FALSE, nml$exp[[iexp]], fcerr)
                }
            }
            xif=xilf
            if (time_order == "2" || time_order == "1,2") {
                nml$inpf=nml$xif
                labargs$labargs2$emu=FALSE
            }
        }
    }
    })
    # starting points and jacobians
    with(e, {
    # prepare series of starting points
    if (nchar(fseries) > 0) {
       pstart=as.matrix(read.table(file.path(dirw, fseries), header=TRUE, row.names=1L, sep="\\t"))
       # skip parameters (rows) who's name is not in nm$param
       i=rownames(pstart) %in% nml$param
       if (!any(i)) {
          stop_mes("Option --fseries is used but no free parameter with known name is found.\\n", file=fcerr)
       }
       pstart=pstart[i,,drop=FALSE]
       cat("Using starting values form '", fseries, "' for the following free parameters:\n", paste(rownames(pstart), collapse="\n"), "\n", sep="", file=fclog)
       nseries=ncol(pstart)
       if (initrand) {
          # fill the rest of rows with random values
          i=nml$param %in% rownames(pstart)
          n=sum(!i)
          pstart=rbind(pstart, structure(matrix(runif(n*nseries), n, nseries), dimnames=list(NULL, sprintf(paste0("V%0", ceiling(log10(nseries+1)), "d"), seq(nseries)))))
          rownames(pstart)=c(rownames(pstart)[seq_len(nbl$param-n)], nml$param[!i])
       }
       if (nchar(iseries) > 0L) {
          iseries=unique(as.integer(eval(parse(t="c("%s+%iseries%s+%")"))))
          iseries=iseries[iseries<=nseries]
          # subsample
          pstart=pstart[,iseries, drop=FALSE]
          nseries=ncol(pstart)
       } else {
          iseries=seq_len(nseries)
       }
    } else if (nchar(iseries) > 0) {
       # first construct pstart then if needed fill it with random values
       # and only then subsample
       iseries=unique(as.integer(eval(parse(t="c(" %s+% iseries %s+%" )"))))
       nseries=max(iseries)
       pstart=matrix(rep(param, nseries), nrow=nbl$param, ncol=nseries)
       dimnames(pstart)=list(nml$param, sprintf(paste0("V%0", ceiling(log10(nseries+1)), "d"), seq(nseries)))
       # subsample
       pstart=pstart[,iseries, drop=FALSE]
    } else {
       iseries=1L
       pstart=as.matrix(param)
    }
    if (initrand) # fill pstart with random values
        pstart[]=runif(length(pstart))
    nseries=ncol(pstart)
    nml$pseries=rownames(pstart)

    if (is.null(nseries) || nseries==0)
       stop_mes("No starting values",  file=fcerr)

    pres=matrix(NA, nbl$param, nseries)
    rownames(pres)=nml$param
    colnames(pres)=colnames(pstart)
    costres=rep.int(NA, nseries)

    # prepare flux index conversion
    ifwrv=seq_len(nbl$fwrv)
    names(ifwrv)=nml$fwrv
    ifl_in_fw=if (nbl$fl) ifwrv[paste("fwd", substring(nml$fl, 4L), sep="")] else integer(0)
    iff_in_fw=if (nbl$ff > 0) ifwrv[paste("fwd", substring(nml$ff, 4L), sep="")] else integer(0)
    ifg_in_fw=if (nbl$fgr > 0) ifwrv[paste("fwd", substring(nml$fgr, 4L), sep="")] else integer(0)

    # index couples for jacobian df_dfl, df_dffd
    nbl$cfw_fl=nbl$crv_fl=cbind(ifl_in_fw, seq_len(nbl$fl))
    nbl$cfw_ff=nbl$crv_ff=cbind(iff_in_fw, seq_len(nbl$ff))
    nbl$cfw_fg=nbl$crv_fg=cbind(ifg_in_fw, nbl$ff+seq_len(nbl$fgr))
    nbl$crv_fl[,1L]=(nbl$fwrv/2)+nbl$crv_fl[,1L]
    nbl$crv_ff[,1L]=(nbl$fwrv/2)+nbl$crv_ff[,1L]
    nbl$crv_fg[,1L]=(nbl$fwrv/2)+nbl$crv_fg[,1L]

    nbl$c_x=c(0, cumsum(nbl$x))

    # fixed part of jacobian (unreduced by SD)
    # measured fluxes
    dufm_dp=cbind(dufm_dff(nbl, nml), matrix(0, nrow=nbl$fmn, ncol=nbl$poolf))
    dimnames(dufm_dp)=list(nml$fmn, nml$param)

    # measured pools
    dupm_dp=matrix(0., nbl$poolm, nbl$ff)
    if (nbl$poolf > 0L)
        dupm_dp=cbind(dupm_dp, measurements$mat$pool[,nml$poolf, drop=FALSE])
    dimnames(dupm_dp)=list(rownames(measurements$mat$pool), nml$param)
    # prepare jacobian env for time_order includes 2
    if (case_i && (time_order == "2" || time_order == "1,2"))
        jx_f2=new.env()

    # formated output in kvh file
    fkvh_saved=if (write_res && wkvh) file.path(dirres, "tmp", sprintf("%s_res.kvh", baseshort))
    retcode=numeric(nseries)
    })
    invisible(NULL)
}
#' make influx_si calculations
#'
#' @param e Environement with all necessary variables and place holders
#' @return None
calc=function(e) {
    # put_inside, zc and init scales
    with(e, {
    for (irun in seq_len(nseries)) {
        top_chrono(sprintf("run %-3d", irun), file=fclog)
        param[nml$pseries]=pstart[nml$pseries, irun]
        runsuf=if (nseries > 1L) "." %s+% colnames(pstart)[irun] else ""
        if (length(nseries) > 0L)
            cat("Starting point", runsuf, "\n", sep="", file=fclog)

        # prepare kvh file name
        fkvh=if (write_res && wkvh) file(substring(fkvh_saved, 1L, nchar(fkvh_saved)-4L) %s+% runsuf %s+% ".kvh", "w")

        # remove zc inequalities from previous runs
        izc=which(startsWith(nml$ineq, "zc "))
        if (length(izc)) {
            ui=ui[-izc,,drop=FALSE]
            ci=ci[-izc]
            nml$ineqi=rownames(ui)
        }
        # check if initial approximation is feasible
        ineq=as.numeric(ui%*%param-ci)
        names(ineq)=rownames(ui)
        # set tolerance for inequality
        tol_ineq=if ("BFGS" %in% methods) 0. else tol
        nbad=sum(ineq <= -tol_ineq)
        if (nbad > 0L) {
            top_chrono("put_ins", file=fclog)
            cat("The following ", nbad, " inequalities are not respected at starting point", runsuf, ":\n", sep="", file=fclog)
            i=ineq[ineq<= -tol_ineq]
            cat(paste(names(i), i, sep="\t", collapse="\n"), "\n", sep="", file=fclog)
            # put them inside
            if (write_res) {
                capture.output(pinside <- put_inside(param, ui, ci), file=fclog)
            } else {
                pinside <- put_inside(param, ui, ci)
            }
            if (any(is.na(pinside))) {
                if (!is.null(attr(pinside, "err")) && attr(pinside, "err")!=0) {
                    # fatal error occured
                    cat("put_inside", runsuf, ": ", attr(pinside, "mes"), "\n", file=fcerr, sep="")
                    retcode[irun]=attr(pinside, "err")
                    next; # next run in iseries
                }
            } else if (!is.null(attr(pinside, "err")) && attr(pinside, "err")==0) {
                # non fatal problem
                cat(paste("***Warning: put_inside: ", attr(pinside, "mes"), collapse=""), "\n", file=fclog)
            }
            param[]=pinside
        }

        # prepare zero crossing strategy
        # inequalities to keep sens of net flux on first call to opt_wrapper()
        # if active they are removed on the second call to opt_wrapper()
        # and finaly all zc constraints are relaxed on the last call to opt_wrapper()
        fallnx=param2fl(param, labargs)$fallnx
        mi_zc=simple_triplet_zero_matrix(0L, nbl$fallnx)
        colnames(mi_zc)=nml$fallnx
        li_zc=NULL
        nmizc=c()
        ifd=which(startsWithv(nml$fallnx, c("d", "f")))
        if (zerocross && length(ifd) > 0L) {
            top_chrono("zc ineq", file=fclog)
            # add lower limits on [df].net >= zc for positive net fluxes
            # and upper limits on [df].net <= -zc for negative net fluxes
            ipos=match(setdiff(names(which(fallnx[ifd]>=0.)), ige), nml$fallnx)
            ineg=match(setdiff(names(which(fallnx[ifd]<0.)), ile), nml$fallnx)
            mi_zc=simple_triplet_zero_matrix(nrow=length(ipos)+length(ineg), ncol=nbl$fallnx)
            colnames(mi_zc)=nml$fallnx
            nmizc=c(nmizc, paste("zc: ", nml$fallnx[ipos], ">=", zc, sep="", recycle0=TRUE))
            mi_zc[cbind(seq_along(ipos), ipos)]=1.
            nmizc=c(nmizc, paste("zc; ", nml$fallnx[ineg], "<=", -zc, sep="", recycle0=TRUE))
            mi_zc[cbind(length(ipos)+seq_along(ineg), ineg)]=-1.
        }
        rownames(mi_zc)=nmizc
        li_zc=rep(zc, length(nmizc)) # that's ok for both pos and neg constraints
        tmp=mi_zc[,nml$fl,drop=FALSE] %stm% (invAfl %stm% pcgc2bfl) # fcgc part of mi
        ui_zc=mi_zc[,nml$ff,drop=FALSE] + tmp[,nml$ff,drop=FALSE]
        ci_zc=li_zc - tmp[,nml$fc,drop=FALSE] %*% fallnx[nml$fc]
        ci_zc=ci_zc - tmp[,colnames(tmp)==""]
        ui_zc=cbind(ui_zc, simple_triplet_zero_matrix(nrow=nrow(mi_zc), ncol=nbl$poolf))
        
        # remove constant inequalities
        zi=if (ncol(ui_zc)) apply(ui_zc,1L,function(v) max(abs(v))<=tol_ineq) else rep(TRUE, nrow(ui_zc))

        inotsat=ci_zc[zi]>tol_ineq
        if (any(inotsat)) {
            cat("***Warning: the following constant zc inequalities are not satisfied:\n", file=fclog)
            cat("\t", nmizc[zi][inotsat], sep="\n\t", file=fclog)
        }
        ui_zc=ui_zc[!zi,,drop=FALSE]
        ci_zc=ci_zc[!zi]
        nmizc=nmizc[!zi]
        mi_zc=mi_zc[!zi,,drop=FALSE]
        ui_zc=as.matrix(ui_zc)

        # remove redundant/contradictory inequalities
        nbzc=nrow(ui_zc)
        nbi=nrow(ui)
        ired=c()
        tui=t(ui)
        uzcd=sapply(seq_len(nbzc), function(i) apply(abs(tui-ui_zc[i,]), 2L, max))
        uzcs=sapply(seq_len(nbzc), function(i) apply(abs(tui+ui_zc[i,]), 2L, max))
        czcd=abs(outer(abs(ci), abs(ci_zc), "-"))
        ired=which(apply((uzcd < tol_ineq | uzcs < tol_ineq) & czcd <= 1.e-2, 2L, any))
          
        if (length(ired) > 0L) {
            # remove all ired inequalities
            cat("The following ", length(ired), " zerocross inequalities are redundant and are removed:\n", paste(nmizc[ired], collapse="\n"), "\n", sep="", file=fclog)
            ui_zc=ui_zc[-ired,,drop=FALSE]
            ci_zc=ci_zc[-ired]
            nmizc=nmizc[-ired]
            mi_zc=mi_zc[-ired,,drop=FALSE]
        }
        if (nrow(ui_zc)) {
            # add zc inequalities
            ui=rbind(ui, ui_zc)
            ci=c(ci, ci_zc)
            nml$ineq=c(nml$ineq, nmizc)
        }
        rm(ui_zc, ci_zc, uzcd, uzcs, czcd)
        rres=NULL
        # see if there are any active inequalities at starting point
        ineq=as.numeric(ui%*%param-ci)
        names(ineq)=rownames(ui)
        nbad=sum(abs(ineq)<=tol_ineq)
        if (nbad > 0)
            cat("The following ", nbad, " inequalities(s) are active at starting point", runsuf, ":\n",
                paste(names(ineq[abs(ineq)<=tol_ineq]), collapse="\n"), "\n", sep="", file=fclog)


        # init kvh writing
        if (write_res && wkvh) {
            top_chrono("kvh init", file=fclog)
            cat("influx\n", file=fkvh)
            cat("\tversion\t", vernum, "\n", file=fkvh, sep="")
            cat("\tlabeling\t", if (case_i) "instationary" else "stationary", "\n", file=fkvh, sep="")
            # save options of command line
            obj2kvh(ropts, "runtime options", fkvh, indent=1L)
            obj2kvh(R.Version(), "R.Version", fkvh, indent=1L)
            cat("\tR command line\n", file=fkvh)
            obj2kvh(opts, "opts", fkvh, indent=2L)
            cat("\t\texecution date\t", format(Sys.time()), " cpu=", proc.time()[1L], "\n", sep="", file=fkvh)
            
            # resume system sizes
            obj2kvh(nbl$sys, "system sizes", fkvh)
            
            # save initial param
            cat("starting point\n", file=fkvh)
            names(param)=nml$param
            obj2kvh(param, "starting free parameters", fkvh, indent=1L)
        }
        
        # main part: call optimization
        # starting res
        if (!length(rres)) {
            rres <- lab_resid(param, cjac=FALSE, labargs)
            if (!is.null(rres$err) && rres$err) {
                cat("lab_resid", runsuf, ": ", rres$mes, "\\n", file=fcerr, sep="")
                retcode[irun]=rres$err
                next
            }
            if (any(is.infinite(rres$res))) {
                cat("At starting point, infinite values appeared in residual vector.", file=fcerr)
                retcode[irun]=1L
                next
            }
        }
        rcost=if (length(rres$res) && !all(ina <- is.na(rres$res))) sum(crossprod(rres$res[!ina])) else NA
        if (write_res && wkvh) {
            obj2kvh(rcost, "starting cost value", fkvh, indent=1L)
            obj2kvh(Afl, "flux system (Afl)", fkvh, indent=1L)
        }
        fg=numeric(nbl$fgr)
        names(fg)=nml$fgr
        if (nbl$fgr > 0)
            fg[paste("g.n.", substring(nml$poolf, 4), "_gr", sep="")]=nbl$mu*param[nml$poolf]
        if (write_res && wkvh) {
            btmp=as.numeric(p2bfl %stm% param[seq_len(nbl$nbl$ff)]+bp+g2bfl %stm% fg)
            names(btmp)=dimnames(Afl)[[1L]]
            obj2kvh(btmp, "flux system (bfl)", fkvh, indent=1L)
        }
        names(param)=nml$param
        if (optimize && nbl$ff+nbl$poolf > 0L) {
            if (!(least_norm || sln || !"nlsic" %in% methods)) {
                # check if at starting position all fluxes can be resolved
                top_chrono("check ja", file=fclog)
                rres=lab_resid(param, cjac=TRUE, labargs)
                if (sum(is.infinite(rres$res))) {
                    cat("Infinite values appeared in residual vector (at identifiability check)", file=fcerr)
                    retcode[irun]=1
                    next
                }
                if (any(is.infinite(rres$jacobian))) {
                    cat("Infinite values appeared in Jacobian (at identifiability check)", file=fcerr)
                    retcode[irun]=1L
                    next
                }
                qrj=qr(jx_f$dr_dff, LAPACK=TRUE)
                d=diag(qrj$qr)
                qrj$rank=sum(abs(d)>abs(d[1L])*tol)
                if (is.na(qrj$rank)) {
                    cat("Rank of starting jacobian could not be estimated.", file=fcerr)
                    retcode[irun]=1L
                    next
                }
                nmuns=if (qrj$rank) nml$ff[qrj$pivot[-(1:qrj$rank)]] else nml$ff
                if (qrj$rank < nbl$ff) {
                    # Too bad. The jacobian of free fluxes is not of full rank.
                    dimnames(jx_f$dr_dff)[[2L]]=c(nml$ffn, nml$ffx)
                    fname="dbg_dr_dff_singular" %s+% runsuf %s+% ".csv"
                    cat(sprintf("Provided measurements (labeling and fluxes) are not sufficient to resolve all free fluxes.\nUnsolvable fluxes may be:\n%s\nJacobian dr_dff is written in the result kvh file (if --wkvh is activated).\n",
                        paste(nmuns, sep=", ", collapse=", ")), file=fcerr)
                    if (write_res && wkvh)
                        obj2kvh(jx_f$dr_dff, "Jacobian dr_dff", fkvh, indent=0)
                    retcode[irun]=1L
                    next
                }
            }
            top_chrono("optim", file=fclog)
            # pass control to the chosen optimization method
            if (time_order=="1,2")
                labargs$time_order="1" # start with order 1, later continue with 2
            for (method in methods) {
                if (write_res) {
                    capture.output(res <- opt_wrapper(param, method, measurements, jx_f, labargs), file=fclog)
                } else {
                    res <- opt_wrapper(param, method, measurements, jx_f, labargs)
                }
                if ((!is.null(res$err) && res$err) || is.null(res$par)) {
                    cat("***Warning: error occured in first optimization pass", runsuf, ": ", res$mes, "\n", sep="", file=fclog)
                    res$par=rep(NA, length(param))
                    res$cost=NA
                } else if (!is.null(res$mes) && nchar(res$mes)) {
                    cat("***Warning: in first optimization pass in run ", runsuf, ": ", res$mes, "\n", sep="", file=fclog)
                }
                if (any(is.na(res$par))) {
                    res$retres$jx_f=NULL # to avoid writing of huge data
                    if (write_res && wkvh)
                        obj2kvh(res, "failed first pass optimization process information", fkvh)
                    cat("Optimization failed", runsuf, ": ", res$mes, "\n", file=fcerr, sep="")
                    # some additional information can be written into fkvh
                    retcode[irun]=max(res$err, 1L)
                    next
                }
                param=res$par
                if (zerocross && !is.null(mi_zc)) {
                    top_chrono("secondzc", file=fclog)
                    # inverse active "zc" inequalities
                    nminv=names(which((ui%*%res$par-ci)[,1L]<=tol_ineq))
                    i=grep("^zc ", nminv, v=TRUE)
                    if (length(i) > 0) {
                        i=str2ind(i, nminv)
                    cat("The following inequalities are active after first pass
        of zero crossing strategy and will be inverted", runsuf, ":\n", paste(nml$ineq[i], collapse="\n"), "\n", sep="", file=fclog)
                        ipos=grep(">=", nml$ineq[i], v=TRUE)
                        ineg=grep("<=", nml$ineq[i], v=TRUE)
                        ui[i,]=-ui[i,,drop=FALSE]
                        if (length(ipos)) {
                            ipzc=str2ind(ipos, nmizc)
                            ipos=str2ind(ipos, nminv)
                            ci[ipos]=as.numeric(zc+mi_zc[ipzc,,drop=FALSE]%*%mic)
                            nml$ineq[ipos]=sub(">=", "<=-", nml$ineq[ipos])
                        }
                        if (length(ineg)) {
                            inzc=str2ind(ineg, nmizc)
                            ineg=str2ind(ineg, nminv)
                            ci[ineg]=as.numeric(zc+mi_zc[inzc,,drop=FALSE]%*%mic)
                            nml$ineq[ineg]=sub("<=-", ">=", nml$ineq[ineg])
                        }
                        rownames(ui)=nminv
                        names(ci)=nminv
                        # enforce new inequalities
                        reopt=TRUE
                        if (write_res) {
                            capture.output(pinside <- put_inside(res$par, ui, ci), file=fclog)
                        } else {
                            pinside <- put_inside(res$par, ui, ci)
                        }
                        if (any(is.na(pinside))) {
                            if (!is.null(attr(pinside, "err")) && attr(pinside, "err")!=0) {
                                # fatal error occured, don't reoptimize
                                cat(paste("put_inside", runsuf, ": ", attr(pinside, "mes"), "\n", collapse=""), file=fcerr)
                                reopt=FALSE
                            }
                        } else if (!is.null(attr(pinside, "err")) && attr(pinside, "err")==0){
                            # non fatal problem
                            cat(paste("***Warning: put_inside", runsuf, ": ", attr(pinside, "mes"), "\n", collapse=""), file=fclog)
                        }
                        # reoptimize
                        if (reopt) {
                            cat("Second zero crossing pass", runsuf, "\n", sep="", file=fclog)
                            if (write_res) {
                                capture.output(reso <- opt_wrapper(pinside, method, measurements, new.env(), labargs), file=fclog)
                            } else {
                                reso <- opt_wrapper(pinside, method, measurements, new.env(), labargs)
                            }
                            if (reso$err || is.null(reso$par)) {
                                cat("***Warning: error in second zero crossing pass: ", reso$mes, "\n", sep="", file=fclog)
                            } else if (!is.null(reso$mes) && nchar(reso$mes)) {
                                cat("***Warning: second zero crossing pass", runsuf, ": ", reso$mes, "\n", sep="", file=fclog)
                            }
                            if(!reso$err && !is.null(reso$par) && !any(is.na(reso$par))) {
                                param=reso$par
                                res=reso
                                jx_f=labargs$jx_f
                            }
                            if (any(is.na(reso$par))) {
                                reso$retres$jx_f=NULL # to avoid writing of huge data
                                if (write_res && wkvh)
                                    obj2kvh(reso, "failed second pass optimization process information", fkvh)
                                cat("***Warning: second zero crossing pass failed. Keep free parameters from previous pass", runsuf, "\n", file=fclog, sep="")
                            }
                        }
                        # last pass, free all zc constraints
                        i=grep("^zc ", nminv)
                        if (length(i) > 0) {
                            top_chrono("last zc", file=fclog)
                            ui=ui[-i,,drop=FALSE]
                            ci=ci[-i]
                            nminv=nml$ineq[-i]
                            cat("Last zero crossing pass (free of zc constraints)", runsuf, "\n", sep="", file=fclog)
                            if (write_res) {
                                capture.output(reso <- opt_wrapper(param, method, measurements, new.env(), labargs), file=fclog)
                            } else {
                                reso <- opt_wrapper(param, method, measurements, new.env(), labargs)
                            }
                            if (reso$err || is.null(reso$par) || (!is.null(res$mes) && nchar(res$mes)))
                                cat("***Warning: last zero crossing (free of zc)", runsuf, ": ", reso$mes, "\n", sep="", file=fclog)
                            if(!reso$err && !is.null(reso$par) && !any(is.na(reso$par))) {
                                param=reso$par
                                res=reso
                                jx_f=labargs$jx_f
                            }
                            if (any(is.na(res$par))) {
                                res$retres$jx_f=NULL # to avoid writing of huge data
                                if (write_res && wkvh)
                                    obj2kvh(res, "failed last pass optimization process information", fkvh)
                                cat("***Warning: last zero crossing pass failed. Keep free parameters from previous passes", runsuf, "\n", file=fclog, sep="")
                            }
                        }
                    } else {
                        cat("After the first optimization, no zero crossing inequality was activated. So no reoptimization", runsuf, "\n", sep="", file=fclog)
                    }
                } # end if zero crossing
            } # for method
            param=res$par
            names(param)=nml$param
            if (excl_outliers != FALSE) {
                # detect outliers
                top_chrono("outliers", file=fclog)
                iva=!is.na(res$res)
                zpval=rz.pval.bi(res$res)
                iout=which(zpval <= excl_outliers & iva)
                #cat("iout=", iout, "\n", file=fclog)
                if (length(iout)) {
                    measurements$outlier=iout
                    outtab=cbind(residual=res$res[iout], `p-value`=zpval[iout])
                    row.names(outtab)=nml$resid[iout]
                    cat("Excluded outliers at p-value ", excl_outliers, ":\n", sep="", file=fclog)
                    write.table(outtab, file=fclog, append=TRUE, quote=FALSE, sep="\t", col.names=FALSE)
                
                    # optimize with the last method from methods
                    if (write_res) {
                        capture.output(reso <- opt_wrapper(param, tail(methods, 1L), measurements, new.env(), labargs), file=fclog)
                    } else {
                        reso <- opt_wrapper(param, tail(methods, 1L), measurements, new.env(), labargs)
                    }
                    if (reso$err || is.null(reso$par) || (!is.null(reso$mes) && nchar(reso$mes)))
                        cat("***Warning: error without outliers: ", reso$mes, "\n", sep="", file=fclog)
                    if (any(is.na(reso$par))) {
                        cat("***Warning: optimization with outliers excluded has failed", runsuf, "\n", file=fclog, sep="")
                        # continue without outlier exclusion
                        measurements$outlier=NULL
                    } else {
                        res=reso
                        param=reso$par
                        names(param)=nml$param
                        jx_f=labargs$jx_f
                        labargs$measurements=measurements # store outliers
                        if (write_res && wkvh)
                            obj2kvh(outtab, "excluded outliers", fkvh)
                    }
                } else {
                    cat("***Warning: outlier exclusion at p-value "%s+%excl_outliers%s+%" has been requested but no outlier was detected at this p-value threshold.", "\n", sep="", file=fclog)
                }
            }
            if (case_i && time_order=="1,2") {
                top_chrono("order 2", file=fclog)
                labargs$time_order="2" # continue with the 2-nd order
                if (write_res) {
                    capture.output(reso <- opt_wrapper(param, tail(methods, 1L), measurements, new.env(), labargs), file=fclog)
                } else {
                    reso <- opt_wrapper(param, tail(methods, 1L), measurements, new.env(), labargs)
                }
                if (reso$err || is.null(reso$par) || (!is.null(reso$mes) && nchar(reso$mes)))
                    cat("***Warning: order2: ", reso$mes, "\n", sep="", file=fclog)
                if (any(is.na(reso$par))) {
                    cat("***Warning: optimization time_order 2 (in '1,2' suite) has failed, run=", runsuf, "\n", file=fclog, sep="")
                } else {
                    res=reso
                    param=reso$par
                    names(param)=nml$param
                    jx_f=labargs$jx_f
                }
            }
            
            if (write_res && wkvh) {
                optinfo=list(
                    "fitted parameters"=param,
                    "last increment before backtracking"=res$lastp,
                    "last increment after backtracking"=res$laststep,
                    "iteration number"=res$it,
                    "convergence history"=res$hist,
                    "exit message"=res$mes
                )
                obj2kvh(optinfo, "optimization process information", fkvh)
            }
            rres=res$retres
        } else {
            top_chrono("resid jac", file=fclog)
            rres=lab_resid(param, cjac=TRUE, labargs)
        }
        top_chrono("postopt", file=fclog)
        # active constraints
        if (!all(is.na(param))) {
            ine=as.numeric(abs(ui%*%param-ci))<tol_ineq
            if (any(ine) && write_res && wkvh)
                obj2kvh(nml$ineq[ine], "active inequality constraints", fkvh)
        }
        poolall[nml$poolf]=param[nml$poolf]

        if (is.null(jx_f$jacobian)) {
            # final jacobian calculation
            if (write_res) {
                capture.output(rres <- lab_resid(param, cjac=TRUE, labargs), file=fclog)
            } else {
                rres <- lab_resid(param, cjac=TRUE, labargs)
            }
            if (!is.null(rres$err) && rres$err) {
                cat("lab_resid", runsuf, ": ", rres$mes, "\n", file=fcerr, sep="")
                retcode[irun]=rres$err
                next
            }
        }
        rcost=cumo_cost(param, labargs, rres)
        pres[,irun]=param
        costres[irun]=rcost
        if (write_res) {
            if (wkvh) obj2kvh(rcost, "final cost", fkvh)
            resid=list()
            # get z p-values on residual vector
            zpval=rz.pval.bi(rres$res)
            resid[["labeled data"]]=i_lapply(jx_f$reslab, function(iexp, rl) if (is.matrix(rl)) rl else cbind(residual=rl, `p-value`=zpval[seq_along(rl)]))
      
            if (case_i)
                resid[["labeled data p-value"]]=lapply(jx_f$reslab, function(mtmp) {mtmp[]=zpval[seq_along(mtmp)]; mtmp})

            nbreslab_tot=sum(lengths(jx_f$reslab))
            if (length(jx_f$resflu))
                resid[["measured fluxes"]]=cbind(residual=jx_f$resflu, `p-value`=zpval[nbreslab_tot+seq_along(jx_f$resflu)])
            if (length(jx_f$respool))
                resid[["measured pools"]]=cbind(residual=if (is.matrix(jx_f$respool)) jx_f$respool[,1L] else jx_f$respool, `p-value`=zpval[nbreslab_tot+length(jx_f$resflu)+seq_along(jx_f$respool)])
            if (wkvh)
                obj2kvh(resid, "(simulated-measured)/sd_exp", fkvh)

            # simulated measurements -> out
            simul=list()
            if (case_i) {
                if (addnoise) {
                    simul[["labeled data"]]=lapply(seq_len(nbl$exp), function(iexp) jx_f$usm[[iexp]]+rnorm(length(jx_f$usm[[iexp]]))*measurements$dev$labeled[[iexp]])
                    names(simul[["labeled data"]])=nml$exp
                } else {
                    # move mass in usm into valid interval [0, 1] and sum=1
                    simul[["labeled data"]]=lapply(seq_len(nbl$exp), function(iexp) {
                        x=clamp(jx_f$usm[[iexp]], 0., 1.)
                        # get unique mass names to sum up to 1
                        nmx=rownames(x)
                        nmm=nmx[startsWith(nmx, "m:")]
                        if (length(nmm)) {
                            # get unique fragments
                            fr_u=unique(sapply(strsplit(nmm, ":", fixed=TRUE), function(v) paste0(c(v[1L:3L], ""), collapse=":")))
                            lapply(fr_u, function(nm) {
                                # get indexes per fragment
                                i=which(startsWith(nmx, nm))
                                mets=strsplit(nm, ":", fixed=TRUE)[[1L]][2L]
                                met1=strsplit(mets, "+", fixed=TRUE)[[1L]][1L]
                                if (length(i) < clen[met1]+1)
                                    return(NULL)
                                s=colSums(x[i,,drop=FALSE])
                                x[i,] <<- arrApply::arrApply(x[i,,drop=FALSE], 2, "multv", v=1./s)
                                NULL
                            })
                        }
                        x
                    })
                    names(simul[["labeled data"]])=nml$exp
                }
                # simul --> .miso.sim
                mlp2LAB=c(m="MS", l="LAB", p="PEAK")
                cnm=c("Id", "Comment", "Specie", "Fragment", "Dataset", "Isospecies", "Value", "SD", "Time", "Residual", "Pvalue")
                for (iexp in seq_len(nbl$exp)) {
                    fnm=nml$exp[[iexp]]
                    rnm=gsub("#", "", nml$meas[[iexp]], fixed=TRUE)
                    mnm=strsplitlim(rnm, ":", fixed=TRUE, lim=NA, strict=TRUE)
                    mnm=matrix(unlist(mnm), ncol=length(mnm[[1L]]), byrow=TRUE)
                    ct=rep(colnames(simul[["labeled data"]][[iexp]]), each=nrow(simul[["labeled data"]][[iexp]]))
                    c3=suppressWarnings(as.integer(mnm[, 3L]))
                    df=cbind(
                        "",
                        "",
                        Specie=mnm[, 2L],
                        Fragment=ifelse(mnm[, 1L] == "m", mnm[, 3L], ""),
                        Dataset=paste0(mlp2LAB[mnm[, 1L]], "_", mnm[, 2L], "_", mnm[, 3L]),
                        Isospecies=ifelse(mnm[, 1L] == "m",
                            paste0("M", mnm[, 4L]), # MS: M0, M1, etc
                            ifelse(mnm[, 1L] == "l", mnm[, 3L], # label: 01x+00x etc
                            paste0(mnm[, 3L], "->", # peak: 2->1,3 etc.
                            ifelse(mnm[, 4L] == "S", "",
                            ifelse(mnm[, 4L] == "D-", c3-1,
                            ifelse(mnm[, 4L] == "D+", c3+1,
                            paste0(c3-1L, ",", c3+1L) # DD
                        )))))),
                        Value=c(simul[["labeled data"]][[iexp]]),
                        SD=measdev[[iexp]],
                        Time=ct,
                        Resid=c(resid[["labeled data"]][[iexp]]),
                        Pvalue=c(resid[["labeled data p-value"]][[iexp]])
                    )
                    colnames(df)=cnm
                    write.table(df, sep="\t", quote=FALSE, row.names=FALSE, fileEncoding="utf8", file=file.path(dirres, paste0(fnm, runsuf, ".miso.sim")))
                }
            } else {
                if (addnoise) {
                    simlab=lapply(seq_len(nbl$exp), function(iexp) jx_f$simlab[[iexp]]+rnorm(length(jx_f$simlab[[iexp]]))*measurements$dev$labeled[[iexp]])
                    names(simlab)=nml$exp
                } else {
                    simlab=jx_f$simlab
                    names(simlab)=nml$exp
                }
                if (nbl$sc_tot > 0) {
                    simul[["labeled data (unscaled)"]]=jx_f$usimlab
                    simul[["labeled data (scaled)"]]=simlab
                } else {
                    simul[["labeled data"]]=simlab
                }
                # simlab --> .miso.sim
                mlp2LAB=c(m="MS", l="LAB", p="PEAK")
                cnm=c("Id", "Comment", "Specie", "Fragment", "Dataset", "Isospecies", "Value", "SD", "Time", "Residual", "Pvalue")
                for (iexp in seq_len(nbl$exp)) {
                    fnm=nml$exp[[iexp]]
                    rnm=gsub("#", "", nml$meas[[iexp]], fixed=TRUE)
                    mnm=strsplitlim(rnm, ":", fixed=TRUE, lim=NA, mat=TRUE)
                    c3=suppressWarnings(as.integer(mnm[, 3L]))
                    df=cbind(
                        "",
                        "",
                        Specie=mnm[, 2L],
                        Fragment=ifelse(mnm[, 1L] == "m", mnm[, 3L], ""),
                        Dataset=paste0(mlp2LAB[mnm[, 1L]], "_", mnm[, 2L], "_", mnm[, 3L]),
                        Isospecies=ifelse(mnm[, 1L] == "m",
                            paste0("M", mnm[, 4L]), # MS: M0, M1, etc
                            ifelse(mnm[, 1L] == "l", mnm[, 3L], # label: 01x+00x etc
                            paste0(mnm[, 3L], "->", # peak: 2->1,3 etc.
                            ifelse(mnm[, 4L] == "S", "",
                            ifelse(mnm[, 4L] == "D-", c3-1L,
                            ifelse(mnm[, 4L] == "D+", c3+1L,
                            paste0(c3-1, ",", c3+1L) # DD
                        )))))),
                        Value=simlab[[iexp]],
                        SD=measdev[[iexp]],
                        Time="",
                        resid[["labeled data"]][[iexp]]
                    )
                    colnames(df)=cnm
                    write.table(df, sep="\t", quote=FALSE, row.names=FALSE, fileEncoding="utf8", file=file.path(dirres, paste0(fnm, runsuf, ".miso.sim")))
                }
            }
            if (nbl$fmn) {
                if (addnoise)
                    simul[["measured fluxes"]]=jx_f$simfmn+rnorm(length(jx_f$simfm))*measurements$dev$flux
                else
                    simul[["measured fluxes"]]=jx_f$simfmn
                # measured fluxes --> .mflux
                cnm=c("Id", "Comment", "Flux", "Value", "SD", "Residual", "Pvalue")
                df=structure(cbind("", "", substring(names(simul[["measured fluxes"]]), 5L), simul[["measured fluxes"]], measurements$dev$flux, resid[["measured fluxes"]]), dimnames=list(NULL, cnm))
                write.table(df, sep="\t", quote=FALSE, row.names=FALSE, file=file.path(dirres, paste0(baseshort, runsuf, ".mflux.sim")))
            }
            if (nbl$poolm) {
                if (addnoise)
                    simul[["measured pools"]]=jx_f$simpool+rnorm(length(jx_f$simpool))*measurements$dev$pool
                else
                    simul[["measured pools"]]=jx_f$simpool
                # measured metabolites --> .mmet
                cnm=c("Id", "Comment", "Specie", "Value", "SD", "Residual", "Pvalue")
                df=structure(cbind("", "", substring(names(simul[["measured pools"]]), 4L), simul[["measured pools"]], measurements$dev$pool, resid[["measured pools"]]), dimnames=list(NULL, cnm))
                write.table(df, sep="\t", quote=FALSE, row.names=FALSE, file=file.path(dirres, paste0(baseshort, runsuf, ".mmet.sim")))
            }
            rm(resid, zpval)
            if (wkvh) obj2kvh(simul, "simulated measurements", fkvh)

            # SD -> out
            # get index of non null components
            iget=sapply(names(measurements$dev), function(nm) !is.null(measurements$dev[[nm]]) & nm %in% c("labeled", "flux", "pool"))
            if (wkvh) {
                obj2kvh(measurements$dev[iget], "measurement SD", fkvh)

                # gradient -> kvh
                if (length(jx_f$res) && !all(ina <- is.na(jx_f$res))) {
                    if (any(ina)) {
                        gr=2*as.numeric(crossprod(jx_f$res[!ina], jx_f$jacobian[!ina,,drop=FALSE]))
                    } else {
                        gr=2*as.numeric(crossprod(jx_f$res, jx_f$jacobian))
                    }
                    names(gr)=nml$param
                    obj2kvh(gr, "gradient vector", fkvh)
                }
                colnames(jx_f$udr_dp)=nml$param
                obj2kvh(jx_f$udr_dp, "jacobian dr_dp (without 1/sd_exp)", fkvh)
                # generalized inverse of non reduced jacobian
                if (length(jx_f$udr_dp) > 0L) {
                    svj=svd(jx_f$udr_dp)
                    invj=svj$v%*%(t(svj$u)/svj$d)
                    dimnames(invj)=rev(dimnames(jx_f$udr_dp))
                    obj2kvh(invj, "generalized inverse of jacobian dr_dp (without 1/sd_exp)", fkvh)
                }
            }
        } # endif write_res

        getx=TRUE
        if (fullsys) {
            nbl$xif=length(xif[[1L]])
            if (case_i && !is.null(cl))
                clusterExport(cl, c("labargs"))
            v=lab_sim(param, cjac=FALSE, labargs, fullsys)
            if (identical(v$err, 1L))
               stop_mes("fullsys: weight=", v$iw, "; ", v$mes, file=fcerr)
            x=if (case_i) v$xf else v$x
        } else {
            v=lab_sim(param, cjac=FALSE, labargs)
            x=if (case_i) v$xf else v$x
        }
        mid=cumo2mass(x)
        if (case_i) {
            mid=lapply(mid, function(m) m[sort(rownames(m)),,drop=FALSE])
        } else if (length(mid)) {
            mid=mid[sort(rownames(mid)),,drop=FALSE]
        }
        # write some info in result kvh
        if (write_res && wkvh) {
            obj2kvh(mid, "MID vector", fkvh)
            # constrained fluxes to kvh
            obj2kvh(fallnx[nml$fc], "constrained net-xch01 fluxes", fkvh)
        }
        fwrv=v$lf$fwrv
        fallnx=v$lf$fallnx
        flnx=v$lf$flnx
        fgr=fallnx[nml$fgr]

        # keep last jx_f in jx_f_last
        while (sensitive=="mc" && !all(is.na(param))) {
            top_chrono("monte-ca", file=fclog)
            if (set_seed)
                set.seed(seed)
            # reference simulation corresponding to the final param
            refsim=new.env()
            for (nmit in c("simlab", "simfmn", "simpool", "usm"))
                assign(nmit, jx_f[[nmit]], envir=refsim)
            # Monte-Carlo simulation in parallel way (if asked and possible)
            if (np > 1L) {
                spli=splitIndices(nmc, nodes);
                clusterExport(cl, c("param", "refsim", "runsuf", "spli"))
                cl_res=clusterEvalQ(cl, {mc_iter=TRUE; labargs$getx=FALSE; mc_res=lapply(spli[[idw]], mc_sim); rm(mc_iter); mc_res})
                mc_res=vector(nmc, mode="list")
                for (i in seq(nodes))
                    mc_res[spli[[i]]]=cl_res[[i]]
            } else {
                mc_res=lapply(seq_len(nmc), function(imc) cl_worker(funth=mc_sim, argth=list(imc)))
            }
            free_mc=sapply(mc_res, function(l) {if (class(l)=="character" || is.null(l) || is.na(l$cost) || l$err) { ret=rep(NA, nbl$param+3) } else { ret=c(l$cost, l$it, l$normp, l$par) }; ret })
            if (length(free_mc)==0) {
                cat("***Warning: parallel exectution of Monte-Carlo simulations has failed.", "\n", sep="", file=fclog)
                free_mc=matrix(NA, nbl$param+2L, 0L)
            }
            cost_mc=free_mc[1L,]
            nmc_real=nmc-sum(is.na(free_mc[4L,]))
            if (write_res && wkvh) {
                cat("monte-carlo\n", file=fkvh)
                indent=1L
                obj2kvh(cl_type, "cluster type", fkvh, indent)
                obj2kvh(avaco, "detected cores", fkvh, indent)
                avaco=max(1L, avaco, na.rm=TRUE)
                obj2kvh(min(avaco, np, na.rm=TRUE), "used cores", fkvh, indent)
                cat("\tfitting samples\n", file=fkvh)
                indent=2L
                obj2kvh(nmc, "requested number", fkvh, indent)
                obj2kvh(nmc_real, "calculated number", fkvh, indent)
                obj2kvh(nmc-nmc_real, "failed to calculate", fkvh, indent)
                # convergence section in kvh
                indent=1
                mout=rbind(round(free_mc[1:2,,drop=FALSE], 2),
                    format(free_mc[3,,drop=FALSE], di=2, sci=TRUE))
                dimnames(mout)=list(c("cost", "it.numb", "normp"), seq_len(ncol(free_mc)))
                obj2kvh(mout, "convergence per sample", fkvh, indent)
            }
            # remove failed m-c iterations
            free_mc=free_mc[-(1:3),,drop=FALSE]
            ifa=which(is.na(free_mc[1,]))
            if (length(ifa)) {
                if (ncol(free_mc) > length(ifa))
                    cat("***Warning: some Monte-Carlo iterations failed.", "\n", sep="", file=fclog)
                free_mc=free_mc[,-ifa,drop=FALSE]
                cost_mc=cost_mc[-ifa]
            }
            if (nmc_real <= 1L) {
                cat("No sufficient Monter-Carlo samples were successfully calculated to do any statistics.", "\n", sep="", file=fcerr)
                retcode[irun]=1
                break
            }
            rownames(free_mc)=nml$param
            # cost section in kvh
            if (write_res && wkvh) {
                cat("\tcost\n", file=fkvh)
                indent=2L
                obj2kvh(mean(cost_mc), "mean", fkvh, indent)
                obj2kvh(median(cost_mc), "median", fkvh, indent)
                obj2kvh(sd(cost_mc), "sd", fkvh, indent)
                obj2kvh(sd(cost_mc)*100./mean(cost_mc), "rsd (%)", fkvh, indent)
                obj2kvh(quantile(cost_mc, c(0.025, 0.95, 0.975)), "ci", fkvh, indent)
                
                # free parameters section in kvh
                cat("\tStatistics\n", file=fkvh)
                mout=c()
                indent=2L
                # param stats
                # mean
                parmean=apply(free_mc, 1L, mean)
                # median
                parmed=apply(free_mc, 1L, median)
                # covariance matrix
                covmc=cov(t(free_mc))
                obj2kvh(covmc, "covariance", fkvh, indent)
                # sd
                sdmc=sqrt(diag(covmc))
                # confidence intervals
                ci_mc=t(apply(free_mc, 1L, quantile, probs=c(0.025, 0.975)))
                ci_mc=cbind(ci_mc, t(diff(t(ci_mc))))
                colnames(ci_mc)=c("CI 2.5%", "CI 97.5%", "CI length")
                mout=cbind(mout, mean=parmean, median=parmed, sd=sdmc,
                   "rsd (%)"=sdmc*100/abs(parmean), ci_mc)
                obj2kvh(mout, "free parameters", fkvh, indent)
                
                # net-xch01 stats
                fallnx_mc=apply(free_mc, 2L, function(p)param2fl(p, labargs)$fallnx)
                fallnx=param2fl(param, labargs)$fallnx
                if (length(fallnx_mc)) {
                    dimnames(fallnx_mc)[[1L]]=nml$fallnx
                    # form a matrix output
                    fallout=matrix(0., nrow=nrow(fallnx_mc), ncol=0L)
                    # mean
                    parmean=apply(fallnx_mc, 1L, mean)
                    # median
                    parmed=apply(fallnx_mc, 1L, median)
                    # covariance matrix
                    covmc=cov(t(fallnx_mc))
                    dimnames(covmc)=list(nml$fallnx, nml$fallnx)
                    # sd
                    sdmc=sqrt(diag(covmc))
                    # confidence intervals
                    cinx_mc=t(apply(fallnx_mc, 1L, quantile, probs=c(0.025, 0.975)))
                    cinx_mc=cbind(cinx_mc, t(diff(t(cinx_mc))))
                    cinx_mc=cbind(cinx_mc, cinx_mc[,3]*100/abs(parmean))
                    colnames(cinx_mc)=c("CI 2.5%", "CI 97.5%", "CI 95% length", "relative CI (%)")
                    fallout=cbind(fallout, mean=parmean, median=parmed, sd=sdmc,
                       "rsd (%)"=sdmc*100/abs(fallnx), cinx_mc)
                    o=order(nml$fallnx)
                    obj2kvh(fallout[o,,drop=FALSE], "all net-xch01 fluxes", fkvh, indent)
                    obj2kvh(covmc[o,o], "covariance of all net-xch01 fluxes", fkvh, indent)
                    
                    # fwd-rev stats
                    fwrv_mc=apply(free_mc, 2, function(p)param2fl(p, labargs)$fwrv)
                    dimnames(fwrv_mc)[[1L]]=nml$fwrv
                    fallout=matrix(0, nrow=nrow(fwrv_mc), ncol=0)
                    # mean
                    parmean=apply(fwrv_mc, 1L, mean)
                    # median
                    parmed=apply(fwrv_mc, 1L, median)
                    # covariance matrix
                    covmc=cov(t(fwrv_mc))
                    dimnames(covmc)=list(nml$fwrv, nml$fwrv)
                    # sd
                    sdmc=sqrt(diag(covmc))
                    # confidence intervals
                    cif_mc=t(apply(fwrv_mc, 1L, quantile, probs=c(0.025, 0.975)))
                    cif_mc=cbind(cif_mc, t(diff(t(cif_mc))))
                    cif_mc=cbind(cif_mc, cif_mc[,3]*100/abs(fwrv))
                    dimnames(cif_mc)[[2L]]=c("CI 2.5%", "CI 97.5%", "CI 95% length", "relative CI (%)")
                    fallout=cbind(fallout, mean=parmean, median=parmed, sd=sdmc,
                       "rsd (%)"=sdmc*100/abs(parmean), cif_mc)
                    o=order(nml$fwrv)
                    obj2kvh(fallout[o,,drop=FALSE], "forward-reverse fluxes", fkvh, indent)
                    obj2kvh(covmc[o,o], "covariance of forward-reverse fluxes", fkvh, indent)
                }
            }
            break
        }
        if (length(sensitive) && nchar(sensitive) && sensitive != "mc") {
            cat(paste("Unknown sensitivity '", sensitive, "' method chosen.", sep=""), "\n", sep="", file=fcerr)
            retcode[irun]=1
            next
        }

        top_chrono("linstats", file=fclog)
        # Linear method based on jacobian x_f
        # reset fluxes and jacobians according to param
        if (is.null(jx_f$jacobian)) {
            if (write_res) {
                capture.output(rres <- lab_resid(param, cjac=TRUE, labargs), file=fclog)
            } else {
                rres <- lab_resid(param, cjac=TRUE, labargs)
            }
            if (!is.null(rres$err) && rres$err) {
                cat("lab_resid", runsuf, ": ", rres$mes, "\n", file=fcerr, sep="")
                retcode[irun]=rres$err
                next
            }
        } # else use the last calculated jacobian

        # covariance matrix of free fluxes
        if (length(jx_f$jacobian) > 0L && !all(is.na(param))) {
            svj=svd(jx_f$jacobian)
            if (svj$d[1L] == 0.) {
                i=rep(TRUE, length(svj$d))
            } else {
                i=svj$d/svj$d[1L]<1.e-10
                if (all(!i) && svj$d[1L]<1.e-10) {
                    # we could not find very small d, take just the last
                    i[length(i)]=TRUE
                }
            }
            ibad=apply(svj$v[, i, drop=FALSE], 2, which.contrib)
            ibad=unique(unlist(ibad))
            if (length(ibad) > 0L)
                cat(paste(if (nchar(runsuf)) runsuf%s+%": " else "", "***Warning: inverse of covariance matrix is numerically singular.\nStatistically undefined parameter(s) seems to be:\n",
                    paste(sort(nml$param[ibad]), collapse="\n"), "\nFor a more complete list, see SD column in '.tvar.sim' result file.", sep=""), "\n", sep="", file=fclog)
            # "square root" of covariance matrix (to preserve numerical positive definitness)
            rtcov=(svj$u)%*%(t(svj$v)/svj$d)
            # standard deviations of free fluxes
            if (write_res) {
                if (wkvh) cat("linear stats\n", file=fkvh)

                # sd free+dependent+growth net-xch01 fluxes
                nml$flfd=c(nml$ff, nml$fgr, nml$fl)
                if (nbl$ff > 0 || nbl$fgr > 0) {
                    i=seq_len(nbl$param)
                    i=c(head(i, nbl$ff), tail(i, nbl$fgr))
                    covfl=crossprod(rtcov[, i, drop=FALSE]%mmt%(rbind(diag(nbl$ff+nbl$fgr), nbl$dfl_dffg)%mrv%c(        rep.int(1., nbl$ff), fgr)))
                    dimnames(covfl)=list(nml$flfd, nml$flfd)
                    sdfl=sqrt(diag(covfl))
                } else {
                    sdfl=rep(0., nbl$fl)
                    covfl=matrix(0., nbl$fl, nbl$fl)
                }
                fl=c(head(param, nbl$ff), fgr, flnx)
                stats_nx=cbind("value"=fl, "sd"=sdfl, "rsd"=sdfl/abs(fl))
                rownames(stats_nx)=nml$flfd
                if (wkvh) {
                    o=order(nml$flfd)
                    obj2kvh(stats_nx[o,,drop=FALSE], "net-xch01 fluxes (sorted by name)", fkvh, indent=1L)
                    obj2kvh(covfl[o, o], "covariance net-xch01 fluxes", fkvh, indent=1L)
                }
             
                # flux, pool --> .tvar
                rnm=grep("_gr$", nml$fallnx, invert=TRUE, value=TRUE)
                cnm=c("Id", "Comment", "Name", "Kind", "Type", "Value", "SD", "Struct_identif")
                if (sensitive == "mc")
                    cnm=c(cnm, "Low_mc", "Up_mc")
                nx2suf=c(n="NET", x="XCH")
                fd2cap=c(f="F", d="D", c="C")

                mnm=matrix(unlist(strsplitlim(rnm, ".", fixed=TRUE, lim=3L)), ncol=3L, byrow=TRUE)
                o=natorder(mnm[, 3L])
                rnm=rnm[o]
                mnm=mnm[o,,drop=FALSE]
                vfl=fallnx[rnm]
                vfl=ifelse(mnm[,2L] == "x", clamp(vfl, 0., 1.), vfl)
                vsd=sdfl[rnm]
                vsd[is.na(vsd)]=0.
                df=cbind("", "", mnm[, 3L], nx2suf[mnm[, 2L]], fd2cap[mnm[, 1L]], vfl, vsd, ifelse(vsd > 10000, "no", "yes"))
                if (sensitive == "mc")
                    df=cbind(df, cinx_mc[rnm, 1L:2L])

                # sd of all fwd-rev
                if (nbl$ff > 0 || nbl$fgr > 0) {
                    i=seq_len(nbl$param)
                    i=c(head(i, nbl$ff), tail(i, nbl$fgr))
                    covf=crossprod(tcrossprod_simple_triplet_matrix(rtcov[,i, drop=FALSE], jx_f$df_dffp%mrv%c(rep.int(1., nbl$ff), head(poolall[nml$poolf], nbl$fgr))))
                    dimnames(covf)=list(nml$fwrv, nml$fwrv)
                    sdf=sqrt(diag(covf))
                } else {
                    sdf=rep(0., length(fwrv))
                }
                if (wkvh) {
                    mtmp=cbind(fwrv, sdf, sdf/abs(fwrv))
                    dimnames(mtmp)[[2L]]=c("value", "sd", "rsd")
                    o=order(nml$fwrv)
                    obj2kvh(mtmp[o,], "fwd-rev fluxes (sorted by name)", fkvh, indent=1L)
                    if (nbl$ff > 0 || nbl$fgr > 0)
                       obj2kvh(covf, "covariance fwd-rev fluxes", fkvh, indent=1L)
                }
                # pool -> kvh
                sdpf=poolall
                sdpf[]=0.

                if (nbl$poolf > 0) {
                    # covariance matrix of free pools
                    # "square root" of covariance matrix (to preserve numerical positive definitness)
                    poolall[nml$poolf]=param[nml$poolf]
                    # cov poolf
                    covpf=crossprod(rtcov[,nbl$ff+seq_len(nbl$poolf), drop=FALSE])
                    dimnames(covpf)=list(nml$poolf, nml$poolf)
                    sdpf[nml$poolf]=sqrt(diag(covpf))
                }
                if (length(poolall) > 0) {
                    if (wkvh) {
                        mtmp=cbind("value"=poolall, "sd"=sdpf, "rsd"=sdpf/poolall)
                        rownames(mtmp)=nml$poolall
                        o=order(nml$poolall)
                        obj2kvh(mtmp[o,,drop=FALSE], "metabolite pools (sorted by name)", fkvh, indent=1L)
                    }
                    if (nbl$poolf > 0) {
                        o=order(nml$poolf)
                        obj2kvh(covpf[o, o], "covariance free pools", fkvh, indent=1L)
                    }
                    rnm=names(poolall)
                    mnm=matrix(unlist(strsplitlim(rnm, ":", fixed=TRUE, lim=2L)), ncol=2L, byrow=TRUE)
                    o=natorder(mnm[, 2L])
                    rnm=rnm[o]
                    mnm=mnm[o,,drop=FALSE]
                    pfc2cap=c(pf="F", pc="C")
                    vsd=sdpf[rnm]
                    vsd[is.na(vsd)]=0.
                    dfp=cbind("", "", mnm[, 2L], "METAB", pfc2cap[mnm[,1L]], poolall[rnm], vsd, ifelse(vsd >= 10000., "no", "yes"))
                    if (sensitive == "mc") {
                        mci=ci_mc[nml$poolf, 1L:2L]
                        mci=rbind(mci, cbind(poolall[nml$poolc], poolall[nml$poolc]))
                        dfp=cbind(dfp, mci[rnm,])
                    }
                    df=rbind(df, dfp)
                }
                colnames(df)=cnm
                write.table(df, sep="\t", quote=FALSE, row.names=FALSE, file=file.path(dirres, paste0(baseshort, runsuf, ".tvar.sim")))
            }
        }
        # goodness of fit (chi2 test)
        if (length(jx_f$res)) {
            if (is.na(rcost)) {
                cat(sprintf("***Warning: chi2: Reduced cost value is NA. Chi2 test cannot be done.\n"), sep="", file=fclog)
            } else {
                nvres=sum(!is.na(jx_f$res))
                if (nvres > nbl$param) {
                    chi2test=list("chi2 value"=rcost, "data points"=nvres,
                       "fitted parameters"=nbl$param, "degrees of freedom"=nvres-nbl$param)
                    chi2test$`chi2 reduced value`=chi2test$`chi2 value`/chi2test$`degrees of freedom`
                    chi2test$`p-value, i.e. P(X^2<=value)`=pchisq(chi2test$`chi2 value`, df=chi2test$`degrees of freedom`)
                    chi2test$conclusion=if (chi2test$`p-value, i.e. P(X^2<=value)` > 0.95) "At level of 95% confidence, the model does not fit the data good enough with respect to the provided measurement SD" else "At level of 95% confidence, the model fits the data good enough with respect to the provided measurement SD"
                    if (write_res) {
                        if (wkvh) obj2kvh(chi2test, "goodness of fit (chi2 test)", fkvh, indent=1L)
                        fstat=file(file.path(dirres, sprintf("%s%s.stat", baseshort,  runsuf)), "w")
                        df=c(rcost, rcost/(nvres-nbl$param), nvres, nbl$param, nvres-nbl$param, chi2test$`p-value, i.e. P(X^2<=value)`, chi2test$conclusion)
                        names(df)=c("chi2_value", "chi2/df", "number_of_measurements", "number_of_parameters", "degrees_of_freedom", "p-value", "conclusion")
                        write.table(df, sep="\t", quote=FALSE, row.names=TRUE, file=fstat, col.names=FALSE)
                        close(fstat)
                    }
                } else {
                    cat(sprintf("***Warning: chi2: Measurement number %d is lower or equal to parameter number %d. Chi2 test cannot be done.\n", nvres, nbl$param), sep="", file=fclog)
                }
            }
        }
        if (prof)
            Rprof(NULL)
        if (write_res) {
            if (wkvh) close(fkvh)
            # write edge.netflux property
            fedge=file(file.path(dirres, "tmp", sprintf("edge.netflux.%s%s.attrs", baseshort,  runsuf)), "w")
            cat("netflux (class=Double)\n", sep="", file=fedge)
            nmedge=names(edge2fl)
            cat(paste(nmedge, fallnx[edge2fl], sep=" = "), sep="\n" , file=fedge)
            close(fedge)

            # write edge.xchflux property
            fedge=file(file.path(dirres, "tmp",  sprintf("edge.xchflux.%s%s.attrs", baseshort,  runsuf)), "w")
            flxch=paste(".x", substring(edge2fl, 4), sep="")
            ifl=charmatch(flxch, substring(names(fallnx), 2))
            cat("xchflux (class=Double)\n", sep="", file=fedge)
            cat(paste(nmedge, fallnx[ifl], sep=" = "), sep="\n" , file=fedge)
            close(fedge)

            # write node.log2pool property
            if (length(poolall)> 0) {
                fnode=file(file.path(dirres, "tmp", sprintf("node.log2pool.%s%s.attrs", baseshort,  runsuf)), "w")
                cat("log2pool (class=Double)\n", sep="", file=fnode)
                nmnode=substring(names(poolall), 4)
                cat(paste(nmnode, log2(poolall), sep=" = "), sep="\n" , file=fnode)
                close(fnode)
            }
        }
    }
    if (write_res) {
        close(e$fclog)
        close(e$fcerr)
    }
    }) # end with()
    invisible(NULL)
}

#' prepare list of spAbr structure for solving cumomer systems
#'
#' @param sp a list of lists with ind_a, ind_b from kvh input file
#' @param e an environment with variables from kvh input file
#' @return List of sub-lists, one per cumomer weight.
prep_spAbr=function(sp, emu, e) {
    res=lapply(seq_along(sp), function(iw) {
    l=new.env()
    list2env(sp[[iw]], envir=l)
    with(l, {
    w=iw
    nbfwrv=e$nbl$fwrv
    ind_a=s2i(ind_a)
    ind_b=s2i(ind_b)
    nbc=s2i(nbc)
    ba_x=s2i(ba_x) # base of cumomer indexes in incu vector
    nbcl=s2i(nbcl) # number of lighter cumomers
    maxprod=s2i(maxprod)
    if (nbc > 0L) {
        # matrix a
        ind_a=matrix(ind_a, ncol=3L, byrow=TRUE)
        colnames(ind_a)=c("indf", "ir0", "ic0")

        # vector b
        ind_b=matrix(ind_b, ncol=2L+maxprod, byrow=TRUE)
        colnames(ind_b)=c("indf", "irow", paste("indx", seq_len(maxprod), sep=""))

        # jacobian b_x
        iprodx=seq_len(maxprod)
        ind_bx=c()
        for (ix in iprodx) {
            i=ind_b[,2+ix]>ba_x # exclude from differentiation plain input entries
            ind_bx=rbind(ind_bx, ind_b[i,c(1L,2L,ix+2L,2L+iprodx[-ix])]) # move diff var to ic1 place
        }
        if (length(ind_bx)) {
          colnames(ind_bx)=c("indf", "irow", "ic1", sprintf("indx%d", seq_len(maxprod-1L)))
          ind_bx[,"ic1"]=ind_bx[,"ic1"]-ba_x
        }
        # emu case
        if (emu) {
            # cumo weights are always starting from 1 to weight max
            # if there is only one weight (max), the lower weights must be present
            # but corresponding matrices and vectors are of dim=0

            # for iw==1 emu+M1 are identical to cumomers
            # and the system A*x=b for emu+M0 does not change as
            # all fluxes in A and b sum to 0.

            # iw is the resulting fragment length
            nme2iemu=setNames(seq_along(e$nml$inemu), e$nml$inemu)
            nmc=e$nml$incu[c(ind_b[,2L+seq_len(maxprod)])]
            nbind=nrow(ind_b)
            if (iw > 1L && maxprod > 1L) {
                ba_e=1L+e$nbl$xiemu
                # prepare names
                dim(nmc)=c(nbind, maxprod)
                # get fragment length for each ind_x which is product of several terms
                flen=vapply(strsplit(nmc, ":"), function(v) if (length(v) > 1L) e$sumbit(as.numeric(v[2L])) else 0L, 1L)
                dim(flen)=dim(nmc)
                wid=apply(flen, 1L, paste0, collapse=",")
                wdisp=list() # weight dispatcher helper
                iw1=seq_len(iw-1L)
                for (ir in seq_len(nbind)) {
                    v=flen[ir,]
                    if (!is.null(wdisp[[wid[ir]]]))
                       next
                    m=Reduce(e$`%m+%`, v);
                    wdisp[[wid[ir]]]=lapply(iw1, function(i) which(m==i, arr.ind=TRUE)-1L)
                }
            }
            for (iwe in seq_len(iw)) {
                if (iwe == 1L || maxprod == 1L) {
                    # For m+0 (iw=1) vector b is the same in cumo and emu
                    ind_b_emu=cbind(iwe=1, ind_b)
                    ind_b_emu[,3L+iprodx]=nme2iemu[paste(nmc, iw-1L, sep="+")]
                    next
                }
                for (ir in seq_len(nbind)) {
                   addw=wdisp[[wid[ir]]][[iwe-1L]]
                   ie=nme2iemu[paste(rep(nmc[ir,], each=nrow(addw)), addw, sep="+")] # row emu names
                   dim(ie)=c(nrow(addw), maxprod)
                   ind_b_emu=rbind(ind_b_emu, cbind(iwe, ind_b[ir,1L], ind_b[ir,2L], ie))
                }
            }
            ind_b_emu[is.na(ind_b_emu)]=1L # ones stay ones

            # prepare b_x_emu
            ind_bx_emu=c()
            if (length(ind_bx) > 0L) {
               for (ix in iprodx) {
                  i=ind_b_emu[,3L+ix] > ba_e # exclude from differentiation plain input entries
                  ind_bx_emu=rbind(ind_bx_emu, ind_b_emu[i,c(1L:3L,ix+3L,3L+iprodx[-ix]), drop=FALSE]) # move diff var to ic1 place
               }
               if (length(ind_bx_emu)) {
                  colnames(ind_bx_emu)=c("iwe", "indf", "irow", "ic1", sprintf("indx%d", seq_len(maxprod-1L)))
                  ind_bx_emu[,"ic1"]=ind_bx_emu[,"ic1"]-ba_e
                  ind_bx_emu[,"irow"]=ind_bx_emu[,"irow"]+(ind_bx_emu[,"iwe"]-1L)*nbc
               }
            }
        }
    }

    # prepare mumps matrix
    if (nbc == 0L) {
        a=Rmumps$new(integer(0L), integer(0L), double(0L), nbc)
        b=simple_triplet_matrix(i=integer(0L), j=integer(0L), v=double(0L), nrow=nbc, ncol=1L)
    } else {
        stopifnot(is.matrix(ind_a))
        stopifnot(is.matrix(ind_b))
        # prepare sparse xmat where col_sums(xmat) will give a$v
        iv0=ind_a[,"ir0"]+ind_a[,"ic0"]*nbc
        o=order(iv0)
        ind_a=ind_a[o,]
        iv0=iv0[o]
        lrep=lrepx=rle(iv0)
        lrepx$values=seq_along(lrep$values)
        xmat=simple_triplet_matrix(i=unlist(lapply(lrep$lengths, seq_len)),
           j=inverse.rle(lrepx), v=rep(1, length(iv0)))
        iu0=lrep$values
        i=as.integer(iu0%%nbc)
        j=as.integer(iu0%/%nbc)
        a=Rmumps$new(i, j, rep(pi, length(iu0)), nbc)
        if (!is.null(e$control_ftbl$mumps)) {
           lapply(grep("^icntl_", names(e$control_ftbl$mumps), v=TRUE), function(nm) {
              i=suppressWarnings(as.integer(strsplit(nm, "_")[[1L]][2L]))
              v=suppressWarnings(as.integer(control_ftbl$mumps[[nm]]))
              if (!is.na(i) && !is.na(v))
                 a$set_icntl(v, i)
           })
        }
        iadiag=which(i==j)
        # prepare sparse bmat where col_sums(bmat) will give b$v
        if (emu) {
            stopifnot(is.matrix(ind_b_emu))
            iv0=ind_b_emu[,"irow"]+(ind_b_emu[,"iwe"]-1L)*nbc-1L
            nbbcol=w
            o=order(iv0)
            ind_b_emu=ind_b_emu[o,,drop=FALSE]
        } else {
            iv0=ind_b[,"irow"]-1L
            nbbcol=1L
            o=order(iv0)
            ind_b=ind_b[o,,drop=FALSE]
        }
        iv0=iv0[o]
        lrep=lrepx=rle(iv0)
        lrepx$values=seq_along(lrep$values)
        bmat=simple_triplet_matrix(i=unlist(lapply(lrep$lengths, seq_len)),
            j=inverse.rle(lrepx), v=rep(1L, length(iv0)))
        iu0=lrep$values
        i=as.integer(iu0%%nbc)
        j=as.integer(iu0%/%nbc)
        b=simple_triplet_matrix(i=i+1L, j=j+1L, v=rep(pi, length(iu0)), nrow=nbc, ncol=nbbcol)
    }
    }) # end with()
    suppressWarnings(rm(addw, flen, i, j, ie, ir, ix, iw1, iu0, iv0, iprodx, m, maxprod, iwe, o, nbind, nmc, nbbcol, nme2iemu, lrep, lrepx, v, wdisp, wid, envir=l))
    l
    }) # end lapply
}
