#pragma once
#include "CoreMinimal.h"
#include "Sound/SoundBase.h"
// Select a recorded take without repeating the previous take on this actor.
inline USoundBase* PickStationSound(USoundBase* Fallback,const TArray<TObjectPtr<USoundBase>>& Takes,TWeakObjectPtr<USoundBase>& Previous)
{
 TArray<USoundBase*,TInlineAllocator<8>> Valid;
 for(auto S:Takes)if(S)Valid.AddUnique(S.Get());
 if(Valid.Num()>1)Valid.Remove(Previous.Get());
 USoundBase* Result=Valid.IsEmpty()?Fallback:Valid[FMath::RandHelper(Valid.Num())];
 Previous=Result;return Result;
}
