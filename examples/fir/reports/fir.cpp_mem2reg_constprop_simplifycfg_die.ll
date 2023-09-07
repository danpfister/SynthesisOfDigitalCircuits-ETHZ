; ModuleID = 'fir.cpp_mem2reg_constprop_simplifycfg.ll'
source_filename = "src/fir.cpp"
target datalayout = "e-m:e-i64:64-f80:128-n8:16:32:64-S128"
target triple = "x86_64-unknown-linux-gnu"

; Function Attrs: noinline nounwind uwtable
define i32 @_Z3firPiS_(i32* %d_i, i32* %idx) #0 {
entry:
  br label %for.body

for.body:                                         ; preds = %for.body, %entry
  %tmp.02 = phi i32 [ 0, %entry ], [ %add5, %for.body ]
  %i.01 = phi i32 [ 0, %entry ], [ %inc, %for.body ]
  %0 = zext i32 %i.01 to i64
  %arrayidx = getelementptr inbounds i32, i32* %idx, i64 %0
  %1 = load i32, i32* %arrayidx, align 4
  %mul = mul nsw i32 %1, 51
  %sub = sub nsw i32 999, %i.01
  %shr = ashr i32 %sub, 4
  %add = add nsw i32 %shr, 5
  %idxprom1 = sext i32 %add to i64
  %arrayidx2 = getelementptr inbounds i32, i32* %d_i, i64 %idxprom1
  %2 = load i32, i32* %arrayidx2, align 4
  %mul3 = mul nsw i32 %2, 23
  %add4 = add nsw i32 %mul, %mul3
  %add5 = add nsw i32 %tmp.02, %add4
  %inc = add nuw nsw i32 %i.01, 1
  %cmp = icmp ult i32 %inc, 1000
  br i1 %cmp, label %for.body, label %for.end

for.end:                                          ; preds = %for.body
  ret i32 %add5
}

; Function Attrs: noinline norecurse nounwind uwtable
define i32 @main() #1 {
entry:
  %d_i = alloca [1 x [1000 x i32]], align 16
  %idx = alloca [1 x [1000 x i32]], align 16
  call void @srand(i32 13) #3
  br label %for.body

for.body:                                         ; preds = %for.inc10, %entry
  br label %for.body3

for.body3:                                        ; preds = %for.body3, %for.body
  %j.02 = phi i32 [ 0, %for.body ], [ %inc, %for.body3 ]
  %call = call i32 @rand() #3
  %rem = srem i32 %call, 100
  %0 = zext i32 %j.02 to i64
  %arrayidx4 = getelementptr inbounds [1 x [1000 x i32]], [1 x [1000 x i32]]* %d_i, i64 0, i64 0, i64 %0
  store i32 %rem, i32* %arrayidx4, align 4
  %call5 = call i32 @rand() #3
  %rem6 = srem i32 %call5, 100
  %1 = zext i32 %j.02 to i64
  %arrayidx9 = getelementptr inbounds [1 x [1000 x i32]], [1 x [1000 x i32]]* %idx, i64 0, i64 0, i64 %1
  store i32 %rem6, i32* %arrayidx9, align 4
  %inc = add nuw nsw i32 %j.02, 1
  %cmp2 = icmp ult i32 %inc, 1000
  br i1 %cmp2, label %for.body3, label %for.inc10

for.inc10:                                        ; preds = %for.body3
  br i1 false, label %for.body, label %for.end12

for.end12:                                        ; preds = %for.inc10
  br label %for.body16

for.body16:                                       ; preds = %for.body16, %for.end12
  %arraydecay = getelementptr inbounds [1 x [1000 x i32]], [1 x [1000 x i32]]* %d_i, i64 0, i64 0, i64 0
  %arraydecay19 = getelementptr inbounds [1 x [1000 x i32]], [1 x [1000 x i32]]* %idx, i64 0, i64 0, i64 0
  %call20 = call i32 @_Z3firPiS_(i32* nonnull %arraydecay, i32* nonnull %arraydecay19)
  br i1 false, label %for.body16, label %for.end23

for.end23:                                        ; preds = %for.body16
  ret i32 0
}

; Function Attrs: nounwind
declare void @srand(i32) #2

; Function Attrs: nounwind
declare i32 @rand() #2

attributes #0 = { noinline nounwind uwtable "correctly-rounded-divide-sqrt-fp-math"="false" "disable-tail-calls"="false" "less-precise-fpmad"="false" "no-frame-pointer-elim"="true" "no-frame-pointer-elim-non-leaf" "no-infs-fp-math"="false" "no-jump-tables"="false" "no-nans-fp-math"="false" "no-signed-zeros-fp-math"="false" "no-trapping-math"="false" "stack-protector-buffer-size"="8" "target-cpu"="x86-64" "target-features"="+fxsr,+mmx,+sse,+sse2,+x87" "unsafe-fp-math"="false" "use-soft-float"="false" }
attributes #1 = { noinline norecurse nounwind uwtable "correctly-rounded-divide-sqrt-fp-math"="false" "disable-tail-calls"="false" "less-precise-fpmad"="false" "no-frame-pointer-elim"="true" "no-frame-pointer-elim-non-leaf" "no-infs-fp-math"="false" "no-jump-tables"="false" "no-nans-fp-math"="false" "no-signed-zeros-fp-math"="false" "no-trapping-math"="false" "stack-protector-buffer-size"="8" "target-cpu"="x86-64" "target-features"="+fxsr,+mmx,+sse,+sse2,+x87" "unsafe-fp-math"="false" "use-soft-float"="false" }
attributes #2 = { nounwind "correctly-rounded-divide-sqrt-fp-math"="false" "disable-tail-calls"="false" "less-precise-fpmad"="false" "no-frame-pointer-elim"="true" "no-frame-pointer-elim-non-leaf" "no-infs-fp-math"="false" "no-nans-fp-math"="false" "no-signed-zeros-fp-math"="false" "no-trapping-math"="false" "stack-protector-buffer-size"="8" "target-cpu"="x86-64" "target-features"="+fxsr,+mmx,+sse,+sse2,+x87" "unsafe-fp-math"="false" "use-soft-float"="false" }
attributes #3 = { nounwind }

!llvm.module.flags = !{!0}
!llvm.ident = !{!1}

!0 = !{i32 1, !"wchar_size", i32 4}
!1 = !{!"clang version 6.0.1 (http://github.com/llvm-mirror/clang 2f27999df400d17b33cdd412fdd606a88208dfcc) (http://github.com/llvm-mirror/llvm 5136df4d089a086b70d452160ad5451861269498)"}
